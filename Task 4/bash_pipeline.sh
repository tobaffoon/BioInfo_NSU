#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Illegal number of parameters" >&2
    exit 2
fi

refname_regex="^.+\/(.+)\.(fa)$"
seqname_regex="^.+\/(.+)\.(fastq.gz|fastq|fq)$"
if [[ $1 =~ $refname_regex ]]
then
    ref_name="${BASH_REMATCH[1]}"
else
    echo "$1 is not an .fa file" >&2
    exit 1
fi

if [[ $2 =~ $seqname_regex ]]
then
    seq_name="${BASH_REMATCH[1]}"
else
    echo "$2 is not an |.fastq.gz|.fastq|.fq| file" >&2
    exit 1
fi

full_name="${seq_name}_on_${ref_name}"

mkdir -p out
rm -rf out/*

fastqc -o out "$2"
rm "out/${seq_name}_fastqc.zip"

minimap2 -a "$1" "$2" > "out/${full_name}.sam"
samtools view -b "out/${full_name}.sam" -o "out/${full_name}.bam"
samtools flagstat "out/${full_name}.bam" > "out/${full_name}.txt"

quality=$(cat "out/${full_name}.txt" | grep -E "^([[:digit:]]+ \+ [[:digit:]] mapped \([[:digit:]]{,2}\.[[:digit:]]{,2}%)" | cut -d  ' ' -f 5 | tr -d "(%")

if (( $(echo "$quality < 90" | bc) ))
then
    echo "[BAD]: Quality of mapping < 90% (${quality})"
    exit 1
else
    echo "[GOOD]: Quality of mapping is ${quality}%"
fi
samtools sort "out/${full_name}.bam" > "out/${full_name}_sorted.bam"
freebayes -f "$1" "out/${full_name}_sorted.bam" > "out/${full_name}.vcf"

echo "Success. See \".sam\", \".bam\", \".txt\" and \".vcf\" files in out/"
