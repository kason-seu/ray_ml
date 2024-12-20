from model_plat.dag.pipeline import Pipeline
from model_plat.dag.stage import stage


@stage
def stage_1():
    print('Running stage 1')


@stage
def stage_2():
    print('Running stage 2')


@stage
def stage_3():
    print('Running stage 3')


@stage
def stage_4():
    print('Running stage 4')


@stage
def stage_5():
    print('Running stage 5')


@stage
def stage_6():
    print('Running stage 6')


def build_pipeline():
    stage1 = stage_1()
    stage2 = stage_2()
    stage3 = stage_3().after(stage2)
    stage4 = stage_4().after(stage2)
    stage5 = stage_5().after(stage1)
    stage6 = stage_6().after(stage3).after(stage4).after(stage5)

    pipeline = Pipeline()

    pipeline.add_stages([
        stage1, stage2, stage3,
        stage4, stage5, stage6
    ])

    return pipeline


pipeline = build_pipeline()

pipeline.visualize()

pipeline.start()