# coding=utf-8
# Copyright 2020 The TensorFlow Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""GPT-3 few-shot evaluation dataset."""

import os
import json
import gzip
import uuid
from absl import logging
import tensorflow.compat.v2 as tf
import tensorflow_datasets.public_api as tfds

_CITATION = """
@article{brown2020language,
    title={Language Models are Few-Shot Learners},
    author={Tom B. Brown et. al.}
    year={2020},
    eprint={2005.14165},
    archivePrefix={arXiv},
    primaryClass={cs.CL}
}
"""

_DESCRIPTION = """
Synthetic datasets for word scramble and arithmetic tasks described in the paper.
"""

_DATA_URL = "https://github.com/openai/gpt-3/archive/master.zip"

_MODULES = [
    "cycle_letters_in_word",
    "five_digit_addition",
    "five_digit_subtraction",
    "four_digit_addition",
    "four_digit_subtraction",
    "mid_word_1_anagrams",
    "mid_word_2_anagrams",
    "random_insertion_in_word",
    "reversed_words",
    "single_digit_three_ops",
    "six_digit_addition",
    "six_digit_subtraction",
    "sum_of_digits",
    "three_digit_addition",
    "three_digit_subtraction",
    "two_digit_addition",
    "two_digit_multiplication",
    "two_digit_subtraction",
]


class Gpt3(tfds.core.GeneratorBasedBuilder):
  """GPT-3 Dataset."""

  BUILDER_CONFIGS = [
      tfds.core.BuilderConfig(
          name=module,
          version=tfds.core.Version("1.0.0"),
          description=_DESCRIPTION,
      ) for module in _MODULES
  ]

  def _info(self):
    return tfds.core.DatasetInfo(
        builder=self,
        description=_DESCRIPTION,
        features=tfds.features.FeaturesDict({
            "context": tfds.features.Text(),
            "completion": tfds.features.Text(),
        }),
        homepage="https://github.com/openai/gpt-3",
        citation=_CITATION,
    )

  def _split_generators(self, dl_manager):
    """Returns SplitGenerator."""

    data = tfds.download.Resource(
        url=_DATA_URL, extract_method=tfds.download.ExtractMethod.ZIP)
    directory = dl_manager.download_and_extract(data)

    return [
        tfds.core.SplitGenerator(
            name=tfds.Split.TEST,
            gen_kwargs={
                "directory": directory,
                "task": self.builder_config.name,
            }),
    ]

  def _is_gzip_file(self, task):
    return "word" in task

  def _generate_examples(self, directory, task):
    """Yields examples based on directory, task name."""

    path = os.path.join(directory, "gpt-3-master/data/", task + ".jsonl")

    if self._is_gzip_file(task):
      path += ".gz"

    with tf.io.gfile.GFile(path, "rb") as f:
      if self._is_gzip_file(task):
        f = gzip.GzipFile(fileobj=f)

      for line in f:
        yield uuid.uuid4().hex, json.loads(line)