import re, subprocess, shutil, os.path
from pathlib import Path 

from toil.common import Toil
from toil.job import Job

mapped_regex = re.compile(r"\d+\s\+\s\d+\smapped\s\((\d{1,2}\.\d{1,2})%")

def parse_ref_seq_names(ref_path, seq_path):
    refname_regex = re.compile(r"^(.+\/)?(.+)\.fa$")
    result = refname_regex.match(str(ref_path))
    if result is None:
        raise RuntimeError(f"{ref_path} is not an .fa file")
    refname = result.group(2).strip()

    seqname_regex = re.compile(r"^(.+\/)?(.+)\.(fastq.gz|fastq|fq)$")
    result = seqname_regex.match(str(seq_path))
    if result is None:
        raise RuntimeError(f"{seq_path} is not an |.fastq.gz|.fastq|.fq| file")
    seqname = result.group(2).strip()

    return (seqname, refname)

def make_out_dir(job, true_cwd):
   job.log("Running: make_out_dir")
   out_path = Path(true_cwd) / 'out'
   if out_path.exists() and out_path.is_dir():
      shutil.rmtree(out_path)

   out_path.mkdir(exist_ok=True)
   return out_path

def run_fastqc(job, out_path, seq_path, progress_log):
   command = f"fastqc -o \"{out_path}\" \"{seq_path}\" &>>\"{progress_log}\""
   job.log(f"Running: {command}")
   subprocess.run(command, check=True, shell=True)

def clean_fastqc(job, out_path, seq_name):
   job.log("Running: clean_fastqc")
   Path.unlink(out_path / f"{seq_name}_fastqc.zip")

def run_minimap2(job, out_path, file_name, ref_path, seq_path, progress_log):
   sam_path = out_path / f"{file_name}.sam"
   command = f"minimap2 -a \"{ref_path}\" \"{seq_path}\" >\"{sam_path}\" 2>>\"{progress_log}\""

   job.log(f"Running:{command}")
   subprocess.run(command, check=True, shell=True)

   return sam_path

def run_samtools_view(job, sam_path, progress_log):
   bam_path = f"{os.path.splitext(sam_path)[0]}.bam"
   command = f"samtools view -b \"{sam_path}\" -o \"{bam_path}\" &>>\"{progress_log}\""

   job.log(f"Running:{command}")
   subprocess.run(command, check=True, shell=True)

   return bam_path

def run_samtools_flagstat(job, bam_path, progress_log):
   txt_path = f"{os.path.splitext(bam_path)[0]}.txt"
   command = f"samtools flagstat \"{bam_path}\" >\"{txt_path}\" 2>>\"{progress_log}\""

   job.log(f"Running:{command}")
   subprocess.run(command, check=True, shell=True)

   return txt_path

def check_flagstat_quality(filename, progress_log):
  with open(filename, 'r') as f, open(progress_log, 'a') as log:
      for line in f:
          result = mapped_regex.match(line)
          if result is None:
              continue
          
          quality_fp = float(result.group(1).strip())
          if quality_fp < 90:
              print("[BAD]: Quality of mapping < 90%", log)
              return
          else:
              print(f"[GOOD]: Quality of mapping is {result.group(1)}%", log)
              return
          
      print(f'Unable to parse {filename}', log)
      return
  
def run_samtools_sort(job, bam_path, progress_log):
   sorted_bam_path = f"{os.path.splitext(bam_path)[0]}_sorted.bam"
   command = f"samtools sort \"{bam_path}\" >\"{sorted_bam_path}\" 2>>\"{progress_log}\""

   job.log(f"Running:{command}")
   subprocess.run(command, check=True, shell=True)

   return sorted_bam_path
  
def run_freebayes(job, ref_path, sorted_bam_path, progress_log):
   vcf_path = f"{os.path.splitext(sorted_bam_path)[0]}.vcf"
   command = f"freebayes -f \"{ref_path}\" \"{sorted_bam_path}\" >\"{vcf_path}\" 2>>\"{progress_log}\""

   job.log(f"Running:{command}")
   subprocess.run(command, check=True, shell=True)
  
def run_echo_success(job):
   command = "echo \"Success. See \".sam\", \".bam\", \".txt\" and \".vcf\" files in out/\""

   job.log(f"Running:{command}")
   subprocess.run(command, check=True, shell=True)


def main():
   parser = Job.Runner.getDefaultArgumentParser()
   parser.add_argument(
            "reference",
            help="Path to file with reference genome in fasta format",
            type=str,
        )
   parser.add_argument(
            "sequence",
            help="Path to file with sequencing data in fastq format",
            type=str,
        )
   options = parser.parse_args()
   options.clean = "always"

   true_cwd = Path.cwd()
   seq_path = true_cwd / options.sequence
   ref_path = true_cwd / options.reference

   parse_res = parse_ref_seq_names(ref_path, seq_path) # get names of reference and sequence
   seqname = parse_res[0]
   refname = parse_res[1]
   pipeline_name = f"{seqname}_on_{refname}"

   mk_outdir_j = Job.wrapJobFn(make_out_dir, str(true_cwd)) # after that create out dir
   out_path = mk_outdir_j.rv()

   progress_log = true_cwd /"progress.log.txt"
   with open(progress_log, 'w') as _:
      pass

   fastqc_j = mk_outdir_j.addChildJobFn(run_fastqc, out_path, seq_path, progress_log) # and run fastqc on it
   clean_fastqc_j = fastqc_j.addChildJobFn(clean_fastqc, out_path, seqname)

   minimap_j = mk_outdir_j.addChildJobFn(run_minimap2, out_path, pipeline_name, ref_path, seq_path, progress_log)
   sam_view_j = minimap_j.addChildJobFn(run_samtools_view, minimap_j.rv(), progress_log)
   sam_flag_j = sam_view_j.addChildJobFn(run_samtools_flagstat, sam_view_j.rv(), progress_log)

   quality_check_j = sam_view_j.addFollowOnFn(check_flagstat_quality, sam_flag_j.rv(), progress_log)

   sam_sort_j = quality_check_j.addChildJobFn(run_samtools_sort, sam_view_j.rv(), progress_log)
   freebayes_j = sam_sort_j.addChildJobFn(run_freebayes, ref_path, sam_sort_j.rv(), progress_log)

   echo_success_j = freebayes_j.addChildJobFn(run_echo_success)
   clean_fastqc_j.addChild(echo_success_j)

   with Toil(options) as toil:
      if not toil.options.restart:
        toil.start(mk_outdir_j)
      else:
        toil.restart()

if __name__ == "__main__":
    main()