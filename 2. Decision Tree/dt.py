import math
import sys
from collections import defaultdict
# 이 함수는 노드 안의 데이터가 모두 같은 class에 속해있는지를 체크합니다.
def check_same_class(dataset, Class_dict):
    #dataset : 해당 노드의 데이터셋들 Class_dict 분류될 클래스의 이름과, 값을 dictionary 형태로 가짐
    Class_name = list(Class_dict.keys())[0]
    Class_value = list(Class_dict.values())[0]
    check_how_many = {}
    #check_how_many dictionary에 노드안의 데이터가 모두 한 클래스에 속하는지 체크
    for value in Class_value:
        check_how_many[value] = 0
    total = 0
    # 데이터의 class들을 체크하여 전체 데이터 개수와 해당 class값에 속하는 개수가 같으면 그 클래스를 갖는다고 판단
    for data in dataset:
        value = check_how_many[data[Class_name]]
        value = value + 1
        check_how_many[data[Class_name]] = value
        total = total + 1
    # 데이터의 class들을 모두 체크
    for check in check_how_many.values():
        if check is total:
            #total값과 check된 값이 같다면 모두 같은 클래스라고 판단
            return True
    return False

#이 함수는 더이상 남은 attribute가 없어 해당 class를 결정해야 할 때 어떤 class를 고를지 결정하는 함수입니다.
def vote_class(dataset, Class_dict, power_of_class_value):
    Class_name = list(Class_dict.keys())[0]
    Class_value = list(Class_dict.values())[0]
    check_how_many = {}
    # 지역변수 초기화
    for value in Class_value:
        check_how_many[value] = 0
    # Class의 값별로 이 데이터셋에 몇개나 해당 class값을 가지는지 체크
    #예를들어 전체 노드 15개가 yes 8 no 7개라면 {'Yes' : 8, 'No' : 7} 과 같은 값을 구합니다.
    total = 0
    for data in dataset:
        value = check_how_many[data[Class_name]]
        value = value + 1
        check_how_many[data[Class_name]] = value
        total = total + 1
    # 이 밑 부분에서는 미리 구한 class value의 가중치를 이용하여 이 노드의 class value에 따른 개수에 가중치를 곱해줍니다.
    # 에를들어 yes 8 no 6인데, 가중치가 yes : 1 no : 1.5라면 계산결과가 8 : 9가 되어 No를 선택합니다.
    # 가중치는 전체 데이터에서 해당 value에 해당하는 데이터의 개수를 체크하여 전체/해당데이터로 정합니다.
    for value in Class_value:
        check_how_many[value] = check_how_many[value] * power_of_class_value[value]
    max_key = max(check_how_many, key=check_how_many.get)
    # 위의 식으로 구한 값들중 가장 큰 class value를 반환.
    return max_key

#이 함수는 각 attribute value별로 해당하는 데이터가 몇개인지 구합니다.
def calculate_how_many(dataset, attribute_name, attribute_value):
    #초기화
    check_how_many = {}
    #attribute value별로 데이터셋을 돌며 몇개나 있는지 체크
    #예를들어 'color'라는 attribute_name이 있고, value가 'red', 'green, 'blue'라면,
    #{'red': 3, 'green' : 5, 'blue', 1} 과 같은 결과를 구함
    for value in attribute_value:
        check_how_many[value] = 0
    total = 0
    for data in dataset:
        value = check_how_many[data[attribute_name]]
        value = value + 1
        check_how_many[data[attribute_name]] = value
        total = total + 1
    # attribute_value별 데이터셋이 몇개 있는지 체크한것을 반환함과 같이 전체 데이터 개수도 체크합니다.
    return check_how_many, total

# 이 함수는 Info(D)의 값을 구합니다.
def calculate_I(dataset, Class_dict):
    Class_name = list(Class_dict.keys())[0]
    Class_value = list(Class_dict.values())[0]
    check_how_many = calculate_how_many(dataset, Class_name, Class_value)
    ret = 0
    # 각 Class value별로 몇개의 값들이 있는지 체크
    for class_element, number in check_how_many[0].items():
        if number is 0:
            number = 0.001
        ret += -1 * (number/float(check_how_many[1])) * math.log((number/float(check_how_many[1])), 2)
    # info(D) = -(sig(p_i * log_2(p_i))) 에 따라 계산
    return ret

# 이 함수는 info_A(D)의 값을 구합니다.
def calculate_I_attribute(dataset, attribute_name, attribute_value, Class_dict):
    check_how_many = {}
    data_following_attribute = defaultdict(list)
    for value in attribute_value:
        check_how_many[value] = 0
    total = 0

    # 각 attribute_value별로 데이터셋에서 몇개가 해당하는지 개수를 구합니다.
    for data in dataset:
        value = check_how_many[data[attribute_name]]
        value = value + 1
        check_how_many[data[attribute_name]] = value
        data_following_attribute[data[attribute_name]].append(data)
        total = total + 1
    information_along_attribute = 0
    #info_A(D) = sig(|D_j|/|D| * info(D_j) 식에 의해서 값을 구합니다.
    for key, value in data_following_attribute.items():
        information_along_attribute += check_how_many[key]/total * calculate_I(value, Class_dict)
    return information_along_attribute

#이 함수는 splitinfo_A(D) 의 값을 구합니다.
def splitinfo(dataset, attribute_name, value_list, Class_dict):
    check_how_many = calculate_how_many(dataset, attribute_name, value_list)
    total = float(check_how_many[1])
    check_how_many = check_how_many[0]
    # 각 attribute의 value 별로 해당하는 데이터의 개수를 체크
    ret = 0
    # splitinfo_A(D) = -sig(|D_j|/|D| * log_2(|D_j|/|D|
    for value in list(check_how_many.values()):
        if value is 0:
            value = 0.001
        ret += -1 * (value/total) * math.log2(value/total)
    #구해진 값을 리턴
    return ret

# 이 함수는 gini(D)의 값을 구합니다.
def calculate_gini(dataset, Class_dict):
    Class_name = list(Class_dict.keys())[0]
    Class_value = list(Class_dict.values())[0]
    check_how_many = calculate_how_many(dataset, Class_name, Class_value)
    # class value별로 해당하는 것이 몇개나 있는지 체크
    ret = 0
    # gini(D) = 1 - sig(p_j*p_j)의 식에 의한 결과값
    for class_element, number in check_how_many[0].items():
        if number is 0:
            number = 0.001
        ret += -1 * (number/float(check_how_many[1])) * (number/float(check_how_many[1]))
    # 결과값 반환
    return 1 + ret

#이 함수는 gini_A(D)의 값을 구합니다.
def gini_index(dataset, attribute_name, attribute_value, Class_dict):
    check_how_many = {}
    data_following_attribute = defaultdict(list)
    #각 attribute value에 해당하는 데이터 개수 체크
    for value in attribute_value:
        check_how_many[value] = 0
    total = 0
    for data in dataset:
        value = check_how_many[data[attribute_name]]
        value = value + 1
        check_how_many[data[attribute_name]] = value
        data_following_attribute[data[attribute_name]].append(data)
        total = total + 1

    #gini_A(D)의 공식에 의해 결과값 계산
    information_along_attribute = 0
    for key, value in data_following_attribute.items():
        information_along_attribute += check_how_many[key]/total * calculate_gini(value, Class_dict)
    #결과값 반환
    return information_along_attribute

# decision_Tree를 만드는 과정에서 어떤 attribute를 선택해야할지 계산하는 함수
def attribute_selection_method(dataset, attribute_set, Class_dict):
    critarion_by_gain_ratio = {}
    #다양한 방법을 활용했으나 gain_ratio가 가장 정확도가 높아 gain_ratio선택
    #critarion_by_gini = {}
    #critarion = {}
    info_of_dataset = calculate_I(dataset, Class_dict)
    #Info(D)를 구함
    #total_critarion_by_gain_ratio = 0
    #여기에서는 Info_A(D)를 구함
    for attribute_name, value_list in attribute_set.items():
        gain_of_attribute = info_of_dataset - calculate_I_attribute(dataset, attribute_name, value_list, Class_dict)
        critarion_by_gain_ratio[attribute_name] = gain_of_attribute/splitinfo(dataset, attribute_name, value_list, Class_dict)
    #   total_critarion_by_gain_ratio += critarion_by_gain_ratio[attribute_name]
    '''
    info_of_dataset = calculate_gini(dataset, Class_dict)
    total_critarion_by_gini = 0

    for attribute_name, value_list in attribute_set.items():
        critarion_by_gini[attribute_name] = info_of_dataset - gini_index(dataset, attribute_name, value_list, Class_dict)
        total_critarion_by_gini += critarion_by_gini[attribute_name]
    if total_critarion_by_gini == 0:
        critarion = critarion_by_gain_ratio
    elif total_critarion_by_gain_ratio == 0:
        critarion = critarion_by_gini
    else:
        for key, value_gain_raio, value_gini in \
                list(zip(critarion_by_gain_ratio.keys(), critarion_by_gain_ratio.values(), critarion_by_gini.values())):
            critarion[key] = (value_gain_raio/total_critarion_by_gain_ratio + value_gini/total_critarion_by_gini)
    '''
    critarion = critarion_by_gain_ratio
    key = max(critarion, key=critarion.get)
    #가장 높은 값을 갖는 attribute 반환
    return key

# decision_tree를 만드는 함수
def generate_decision_tree(dataset, attribute_dict, Class_dict, power_of_class_value):
    decision_tree = {}
    #만약 데이터셋이 모두 같은 class라면 그 class를 선택
    if check_same_class(dataset, Class_dict):
        what_is_class = vote_class(dataset, Class_dict, power_of_class_value)
        return what_is_class
    # 만약 더이상 선택할 attribute가 없다면 해당 데이터셋의 가장 높은 비중을 차지하는 class value로 선택
    if attribute_dict == {}:
        many_class = vote_class(dataset, Class_dict, power_of_class_value)
        return many_class
    # 어떤 attribute를 선택할지 결정
    selected_attribute_name = attribute_selection_method(dataset, attribute_dict, Class_dict)
    data_along_attribute_value = {}

    #attribute를 결정했으면 value에 따라 분류한뒤 재귀적으로 DT구현
    for attribute_dict_value in attribute_dict[selected_attribute_name]:
        data_along_attribute_value[attribute_dict_value] = []
    attribute_dict.pop(selected_attribute_name)
    #분류하는 loop
    for data in dataset:
        data_along_attribute_value[data[selected_attribute_name]].append(data)
    data_along_attribute_value = dict(data_along_attribute_value)
    data_recursive = {}
    #분류 후 남은 data가 없으면 현재 node의 대표 class value할당, 남은 data가 있으면 재귀적으로 DT생성
    for attribute_value, attribute_data in data_along_attribute_value.items():
        attribute_data = list(attribute_data)
        temp_attribute_dict = attribute_dict.copy()
        if attribute_data == []:
            data_recursive[attribute_value] = vote_class(dataset, Class_dict, power_of_class_value)
        else:
            ret = generate_decision_tree(attribute_data, temp_attribute_dict, Class_dict, power_of_class_value)
            data_recursive[attribute_value] = ret
    decision_tree[selected_attribute_name] = data_recursive
    # 완성된 DT 반환
    return decision_tree

#file 이름 입력받음
TRAIN_FILE_PATH = sys.argv[1]
TEST_FILE_PATH = sys.argv[2]
RESULT_FILE_PATH = sys.argv[3]

#input을 포맷에 맞게 수정후 저장
train_data_file = open(TRAIN_FILE_PATH, 'r')
first_line = train_data_file.readline()
first_line = first_line.strip('\n')
first_line = first_line.split('\t')
all_input_data = train_data_file.readlines()
train_data_file.close()
#input완료
#dataset과 attribute set으로 구분
dataset = []
attribute_set = {}
temp_attribute_set = defaultdict(list)
for input_data in all_input_data:
    input_data = input_data.strip('\n')
    data = input_data.split('\t')
    temp_dict = dict(zip(first_line, data))
    dataset.append(temp_dict)
    for k, v in temp_dict.items():
        temp_attribute_set[k].append(v)

for k, v in temp_attribute_set.items():
    v = list(set(v))
    attribute_set[k] = v
#입력완료, Class 이름과 값 구하여 dictionary로 관리
Class_dict = {}
Class_name = first_line[-1]
Class_dict[Class_name] = attribute_set[Class_name]
attribute_set.pop(Class_name)

#각 attribute의 가중치를 구함
power_of_attribute = calculate_how_many(dataset, Class_name, list(Class_dict.values())[0])
num_of_dataset = power_of_attribute[1]
for k, v in power_of_attribute[0].items():
    power_of_attribute[0][k] = num_of_dataset/v
power_of_class_value = power_of_attribute[0]
#각 attribute의 가중치 구하기 완료
#decision tree 만듦
decision_tree = generate_decision_tree(dataset, attribute_set, Class_dict, power_of_class_value)

#DT완성후 test 시작
test_data_file = open(TEST_FILE_PATH, 'r')
first_line = test_data_file.readline()
first_line = first_line.strip('\n')
first_line = first_line.split('\t')
all_input_data = test_data_file.readlines()
test_data_file.close()

#test파일 입력받고, 포맷에 맞게 저장
test_dataset=[]
for input_data in all_input_data:
    input_data = input_data.strip('\n')
    data = input_data.split('\t')
    temp_dict = dict(zip(first_line, data))
    test_dataset.append(temp_dict)

#data를 테스트하는데 쓰이는 함수, DT가 dictionary형태로 구현되어있어 그에 맞게 재귀함수로 test구현
def data_test(data, decision_tree):
    attribute = list(decision_tree.keys())[0]
    attribute_value_in_data = data[attribute]
    nodes = decision_tree[attribute]
    next_tree = nodes[attribute_value_in_data]
    #해당하는 key를 가지고 트리를 따라 내려가는 형태, 결과가 string이면 classvalue에 도달했다고 생각하고 반환한다.
    if type(next_tree) is str:
        return next_tree
    return data_test(data, next_tree)

#결과값 출력을 위한 작업
end_test_dataset = []
for data in test_dataset:
    data[list(Class_dict.keys())[0]] = data_test(data, decision_tree)
    end_test_dataset.append(data)

#output파일 열기
result_data_file = open(RESULT_FILE_PATH, 'w')
output_str = str
#포맷에 맞게 결과 수정후 파일 출력
for attribute in first_line:
    result_data_file.write(attribute + '\t')
result_data_file.write(list(Class_dict.keys())[0] + '\n')

for data in end_test_dataset:
    for key in first_line:
        result_data_file.write(data[key] + '\t')
    result_data_file.write(data[list(Class_dict.keys())[0]] + '\n')