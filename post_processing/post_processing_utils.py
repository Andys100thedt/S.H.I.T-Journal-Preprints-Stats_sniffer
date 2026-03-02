import numpy,time,sys

from post_processing.stat_accumu import StatFrame,_STATIC_FRAME
from enumerate_configuration import _DEFAULT_CONFIGURATION
from scipy.optimize import curve_fit

def target_log_func(x, a, b):
    return  a*numpy.log(x)+b

def deduce_capped_y(x,coefficients):
    return target_log_func(x,coefficients[0],coefficients[1])

def time_weighted_mse(sorted_dataflow: list[StatFrame]) -> tuple:
    grand_t = sorted_dataflow[-1].timestamp - sorted_dataflow[0].timestamp
    if grand_t == 0:
        print("warn: grand_t=0")
        return 0.0, 0.0

    sorted_ts = [data.timestamp for data in sorted_dataflow]
    sorted_plain = [data.score_plain for data in sorted_dataflow]
    sorted_weighted = [data.score_weighted for data in sorted_dataflow]

    fit_plain = curve_fit(target_log_func,sorted_ts,sorted_plain, maxfev=100000)[0]
    fit_weighted = curve_fit(target_log_func,sorted_ts,sorted_weighted, maxfev=100000)[0]

    accumulated_mutation_plain = 0
    accumulated_mutation_weighted = 0
    accumulated_offset_weighted = 0

    for idx,frame in enumerate(sorted_dataflow):
        if idx == 0: continue
        else:
            dt = frame.timestamp - sorted_dataflow[idx-1].timestamp
            accumulated_mutation_plain += pow(abs(frame.score_plain - deduce_capped_y(frame.timestamp, fit_plain)),2) * dt
            accumulated_mutation_weighted += pow(abs(frame.score_weighted - deduce_capped_y(frame.timestamp, fit_weighted)),2) * dt
            accumulated_offset_weighted += (frame.score_weighted - deduce_capped_y(frame.timestamp, fit_weighted)) * dt

    return accumulated_mutation_weighted / grand_t, accumulated_mutation_plain / grand_t, accumulated_offset_weighted / grand_t

def jump_rate(sorted_dataflow: list[StatFrame]) -> float:
    if len(sorted_dataflow) < 2:
        return 0.0

    total_jump = 0.0
    latest_jump = 0
    for i in range(1, len(sorted_dataflow)):
        jump = sorted_dataflow[i].score_plain - sorted_dataflow[i - 1].score_plain
        total_jump += jump
        if jump > 0:
            latest_jump = sorted_dataflow[i].timestamp

    return total_jump / abs(latest_jump - sorted_dataflow[0].timestamp)

def entropy_weight(data, epsilon=1e-12):
    """
    使用熵权法计算指标权重。

    参数:
    data : array-like, shape (n_samples, n_features)
        输入数据矩阵，每行是一个样本，每列是一个指标。
        要求数据非负（如果需要处理负值，请先进行正向化或平移）。
    epsilon : float, optional
        用于避免 log(0) 的极小值，默认 1e-12。

    返回:
    weights : numpy.ndarray, shape (n_features,)
        每个指标的权重。
    """
    # 转换为 numpy 数组
    x = numpy.array(data)

    # 检查数据维度
    if x.ndim != 2:
        raise ValueError("输入数据必须是二维数组")

    n_samples, n_features = x.shape

    # 步骤1：数据标准化（Min-Max 归一化到 [0, 1]）
    # 注意：如果数据已经非负且量纲一致，可以跳过此步
    min_vals = x.min(axis=0)
    max_vals = x.max(axis=0)
    # 避免除以零：如果某列最大值等于最小值，则标准化后全为0
    ranges = max_vals - min_vals
    ranges[ranges == 0] = 1  # 暂时置1，后续该列将全为0，不影响计算
    x_norm = (x - min_vals) / ranges

    # 步骤2：计算每个指标下各样本的比重 p_ij
    # 按列求和
    col_sums = x_norm.sum(axis=0)
    # 避免除以零：如果某列和为0，则比重全为0
    col_sums[col_sums == 0] = 1
    p = x_norm / col_sums  # shape (n_samples, n_features)

    # 步骤3：计算每个指标的熵值 e_j
    # 计算 p * ln(p)，处理 p=0 的情况（0*ln(0)=0）
    p_log_p = p * numpy.log(p + epsilon)  # 加 epsilon 避免 log(0)
    # 计算熵值
    k = 1.0 / numpy.log(n_samples)  # 当 n_samples=1 时会出现除零，需处理
    if n_samples <= 1:
        raise ValueError("样本数必须大于1才能计算熵值")
    e = -k * numpy.sum(p_log_p, axis=0)

    # 步骤4：计算差异系数 d_j
    d = 1 - e

    # 步骤5：计算权重 w_j
    # 如果所有差异系数都为0（即所有指标值都相等），则权重均分
    if numpy.sum(d) == 0:
        weights = numpy.ones(n_features) / n_features
    else:
        weights = d / numpy.sum(d)

    return weights

def clamp_and_sort(backward_offset:float, dataflow: list[StatFrame]) -> list[StatFrame]:
    sorted_dataflow = sorted(dataflow, key=lambda x: x.timestamp if x.timestamp != -1 else sys.maxsize)
    if backward_offset <= 0: return sorted_dataflow

    if sorted_dataflow[0].rated_count != 0:
        ph_frame = _STATIC_FRAME
        ph_frame.timestamp = sorted_dataflow[0].timestamp - _DEFAULT_CONFIGURATION.interval
        sorted_dataflow.insert(0, ph_frame)

    t_threshold = (time.time() - backward_offset)
    for idx,frame in enumerate(sorted_dataflow):
        if idx == 0: continue
        if (sorted_dataflow[idx-1].timestamp <= t_threshold) and (sorted_dataflow[idx].timestamp > t_threshold):
            # threshold reached
            return sorted_dataflow[idx:-1]
    return []