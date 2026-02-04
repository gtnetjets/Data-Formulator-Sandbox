import pytest

from data_formulator import TransformationPipeline


def test_pipeline_runs_in_order():
    pipeline = TransformationPipeline()
    pipeline.add_step(lambda value: value + 1).add_step(lambda value: value * 2)

    assert pipeline.run(2) == 6


def test_steps_default_isolated_between_instances():
    first = TransformationPipeline()
    second = TransformationPipeline()

    first.add_step(lambda value: value + 10)

    assert second.steps == ()
    assert second.run(5) == 5


def test_steps_iterable_is_copied():
    steps = [lambda value: value + 3]
    pipeline = TransformationPipeline(steps)

    steps.append(lambda value: value * 10)

    assert pipeline.run(1) == 4


def test_clone_produces_independent_pipeline():
    pipeline = TransformationPipeline()
    pipeline.add_step(lambda value: value + 2)

    clone = pipeline.clone()
    clone.add_step(lambda value: value * 3)

    assert pipeline.run(1) == 3
    assert clone.run(1) == 9


def test_rejects_non_callable_steps():
    pipeline = TransformationPipeline()

    with pytest.raises(TypeError):
        pipeline.add_step(42)
