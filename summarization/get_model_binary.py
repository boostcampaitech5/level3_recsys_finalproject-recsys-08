import argparse
from finetune import KoBARTConditionalGeneration
from transformers.models.bart import BartForConditionalGeneration
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("--hparams", default='save/hparams.yaml', type=str)
parser.add_argument("--model_binary", default='save/best_model.ckpt', type=str)
parser.add_argument("--output_dir", default='output', type=str)
args = parser.parse_args()

with open(args.hparams) as f:
    hparams = yaml.full_load(f)

inf = KoBARTConditionalGeneration.load_from_checkpoint(args.model_binary, hparams=hparams)

inf.model.save_pretrained(args.output_dir)

