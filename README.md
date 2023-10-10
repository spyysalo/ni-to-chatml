# Natural Instructions to ChatML

Generate ChatML from Natural Instructions data

## Quickstart

Download recent NI release and unpack

```
wget https://github.com/allenai/natural-instructions/archive/refs/tags/v2.8.tar.gz
tar xzf v2.8.tar.gz
```

Test with a single pseudorandom instance

```
python3 ni_to_chatml.py --seed 42 --max-instances 1 natural-instructions-2.8/tasks/task1564_triviaqa_answer_generation.json
```

output

```
{"id": "task1564-4766d6ece93e43aa8ca43db99854dae4", "text": "<|im_start|>user\nIn this task you are given a question. You need to generate an answer to the question.\nQuestion:In Germany, what is an autobahn?<|im_end|>\n<|im_start|>assistant\nfreeway<|im_end|>"}
```

Convert a sample of instances from all tasks, limiting to selected
languages and excluding test set and translation tasks

```
mkdir natural-instructions-2.8-jsonl

for f in natural-instructions-2.8/tasks/*.json; do
    python3 ni_to_chatml.py \
        --exclude natural-instructions-2.8/splits/default/test_tasks.txt,natural-instructions-2.8/splits/xlingual/test_tasks.txt \
	--languages English,Finnish,Swedish,Norwegian,Danish,Icelandic \
	--skip-translation \
	--max-instances 1000 $f \
	> natural-instructions-2.8-jsonl/$(basename $f .json).jsonl
done
```

Remove empties

```
find natural-instructions-2.8-jsonl -empty | xargs rm
```
