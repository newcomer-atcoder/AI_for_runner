from src.my_modules.ai.models import DefaultModel

def test_inference():
    testModel = DefaultModel()

    testCases = [
        (0, 50), (11, 0), (11, 100), #正常値
        (-1, 50), (11, -1), (11, 101), (1, None) #異常値
    ]

    # result is None?
    exp_results = [False] * 3 + [True] * 4

    #各ケースで推論処理
    for (distance, condition), exp_result in zip(testCases, exp_results):
        print(distance, condition)
        result = testModel.inference(distance, condition)
        assert (result is None) == exp_result