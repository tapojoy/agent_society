import time
import traceback

from .schema import create_collection
from .extract import extract
from .preprocess import preprocess
from .chunk import chunk
from .embedder import embed
from .index import index


PIPELINE = [
    ("Create Schema", create_collection),
    ("Extract", extract),
    ("Preprocess", preprocess),
    ("Chunk", chunk),
    ("Embed", embed),
    ("Index", index),
]


def run_pipeline():

    print("=" * 60)
    print("Starting Offline RAG Pipeline")
    print("=" * 60)

    pipeline_start = time.perf_counter()

    total_stages = len(PIPELINE)

    for stage_no, (name, stage) in enumerate(
        PIPELINE,
        start=1
    ):

        print()
        print(
            f"[{stage_no}/{total_stages}] "
            f"{name}"
        )

        stage_start = time.perf_counter()

        try:

            stage()

        except Exception:

            print()
            print(f"Stage failed: {name}")
            print(traceback.format_exc())

            raise

        elapsed = (
            time.perf_counter()
            - stage_start
        )

        print(
            f"{name} completed "
            f"in {elapsed:.2f}s"
        )

    total_elapsed = (
        time.perf_counter()
        - pipeline_start
    )

    print()
    print("=" * 60)
    print(
        f"Pipeline completed "
        f"in {total_elapsed:.2f}s"
    )
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
