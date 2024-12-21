# Предсказание и парное выравнивание структур белков

## **Входные параметры**
   1. Последовательность: MDADVISFEASRGDLVVLDAIHDARFETEAGPGVYDIHSPRIPSEKEIEDRIYEILDKIDVKKVWINPDCGLKTRGNDETWPSLEHLVAAAKAVRARLDK
   
   2. Программы-предсказатели: OpenFold, OmegaFold

   3. Программа-выравниватель: [jFATCAT-rigid](https://www.rcsb.org/alignment). Изначально я был зарегистрирован на CLICK, но при обращении он выдаёт HTT (внутренняя ошибка сервера).

## **Проемежуточные данные**
|              | [OpenFold](https://colab.research.google.com/github/aqlaboratory/openfold/blob/main/notebooks/OpenFold.ipynb) | [Omegafold](https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/beta/omegafold.ipynb) |
| ------------ | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Ноутбук      | [OpenFold.ipynb](OpenFold.ipynb)                                                                              | [OmegaFold.ipynb](OmegaFold.ipynb)                                                                       |
| Предсказания | [OpenFold.pdb](OpenFold.pdb)                                                                                  | [OmegaFold.pdb](OmegaFold.pdb)                                                                           |
| Выравнивание | [OpenFold.pdb.A.cif](OpenFold.pdb.A.cif)                                                                      | [OmegaFold.pdb.A.cif](OmegaFold.pdb.A.cif)                                                               |

## **Полная выдача программы выравнивания**

1. [OmegaFold.pdb.A.cif](OmegaFold.pdb.A.cif)
2. [OpenFold.pdb.A.cif](OpenFold.pdb.A.cif)
3. [alignment.fasta](alignment.fasta)
4. [transformation_matrices.json](transformation_matrices.json)
5. [Результаты выравнивания](alignment.png)

| Entry         | Chain | RMSD | TM-score | Identity | Aligned Residues | Sequence Length | Modeled Residues |
| ------------- | ----- | ---- | -------- | -------- | ---------------- | --------------- | ---------------- |
| OpenFold.pdb  | A     | -    | -        | -        | -                | 100             | 100              |
| OmegaFold.pdb | A     | 1.11 | 0.93     | 100%     | 99               | 100             | 100              |

## **Сессия из PyMOL**

[Сессия](session.pse)

## **Запись видео с полученным раскрашенным выравниванием**
[Запись](recording.mkv)

## **Краткие выводы о совпадении полученных предсказаний**
В соответствии с результатами выравнивания точность совпадений предсказаний достигает 100%, а показатель TM-score составляет 0.93 (из 1.0), что свидетельствует о практически полной идентичности полученных предсказаний. Это также заметно при визуальном анализе в PyMOL (структуры слегка сдвинуты для предотвращения наложений).