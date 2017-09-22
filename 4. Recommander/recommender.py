import sys
import math

#input
File_path = ""
#argument 들을 통해 file들을 읽는다.
Base_file_path = sys.argv[1]
Test_file_path = sys.argv[2]

#get Base file & test file
Base_input_path = File_path + Base_file_path
base_file = open(Base_input_path, 'r')

base_dataset = []
input_data = base_file.readlines()
# make base dataset
for data in input_data:
    data = data.strip('\n')
    temp_data = []
    temp_data += data.split('\t')

    base_dataset.append(temp_data)
# make test dataset
test_dataset = []
Test_input_path = File_path + Test_file_path
test_file = open(Test_input_path, 'r')
test_data = test_file.readlines()
test_dataset = []
for data in test_data:
    data = data.strip('\n')
    temp_data = []
    temp_data += data.split('\t')

    test_dataset.append(temp_data)

# transform dataset to dictionary format
user_item_dict = dict()
# user_item_dict format
# { 'user_id' : {'item_id' : 'rate', 'item_id' : 'rate', ...}
#     'user_id' : ....}
item_user_dict = dict()
# item_user_dict format
# { 'item_id' : {'user_id' : 'rate', 'user_id' : 'rate', ...}
#     'item_id' : ....}
# making dictionaries
for data in base_dataset:
    inner_dict = dict()
    if user_item_dict.get(data[0]) is None:
        inner_dict[data[1]] = data[2]
        user_item_dict[data[0]] = inner_dict.copy()
    else:
        temp_dict = user_item_dict[data[0]]
        temp_dict[data[1]] = data[2]
        user_item_dict[data[0]] = temp_dict.copy()
    inner_dict.clear()
    if item_user_dict.get(data[1]) is None:
        inner_dict[data[0]] = data[2]
        item_user_dict[data[1]] = inner_dict.copy()
    else:
        temp_dict = item_user_dict[data[1]]
        temp_dict[data[0]] = data[2]
        item_user_dict[data[1]] = temp_dict.copy()

#this function calculate similarity of two users
def sim(x, y, x_dict, y_dict):
    #calculate average rate (r_x)
    total_score = 0
    for data in x_dict.values():
        total_score += int(data)
    avg_score_x = total_score/x_dict.values().__len__()
    total_score = 0
    #calculate average rate (r_y)
    for data in y_dict.values():
        total_score += int(data)
    avg_score_y = total_score/y_dict.values().__len__()

    #get common_items that belongs both x and y
    common_list = list(set(x_dict.keys()).intersection(y_dict.keys()))
    sum_dif_x_y = 0
    rs_x = 0
    rs_y = 0
    # calculate similarity between x and y
    for item in common_list:
        x_score = float(x_dict[item])
        y_score = float(y_dict[item])
        sum_dif_x_y += (x_score - avg_score_x)*(y_score - avg_score_y)
        rs_x += (x_score - avg_score_x)*(x_score - avg_score_x)
        rs_y += (y_score - avg_score_y)*(y_score - avg_score_y)
    # return similarity
    try:
        ret = sum_dif_x_y/(math.sqrt(rs_x)*math.sqrt(rs_y))
    except ZeroDivisionError:
        ret = 0
    return ret

#open output file
Output_file_path = File_path + sys.argv[1][0:2] + '.base_prediction.txt'
output_file = open(Output_file_path, 'w')

#this function calcalate average of rate of user x
def average(x, x_dict):
    total_score = 0
    for data in x_dict.values():
        total_score += int(data)
    return total_score/x_dict.values().__len__()

#make prediction of rate
for data in test_dataset:
    #if nobody evaluate the item, then rate is average of user x`s rate
    if item_user_dict.get(data[1]) is None:
        temp_score = user_item_dict[data[0]].values()
        total_score = 0
        for score in temp_score:
            total_score += int(score)
        avg_score = total_score/temp_score.__len__()
        #write in file
        output_string = data[0] + '\t' + data[1] + '\t' + str(avg_score) + '\n'
        output_file.write(output_string)
    #find users that evaluate the item, and calculate predict rate
    else:
        user_same_item_list = item_user_dict[data[1]].keys()
        total_similarity = 0
        total_sim_r = 0
        # calculate prediction. 식은 보고서에 첨부.
        for user in user_same_item_list:
            similarity = sim(data[0], user, user_item_dict[data[0]], user_item_dict[user])
            total_sim_r += similarity * (int(item_user_dict[data[1]][user]) - average(user, user_item_dict[user]))
            total_similarity += similarity

        pred = average(data[0], user_item_dict[data[0]]) + total_sim_r/total_similarity
        #if prediction is improper, rate is average of rate of user x
        if pred < 0 or pred >= 5:
            pred = average(data[0], user_item_dict[data[0]])
        #write in file
        output_string = data[0] + '\t' + data[1] + '\t' + str(pred) + '\n'
        output_file.write(output_string)
output_file.close()
