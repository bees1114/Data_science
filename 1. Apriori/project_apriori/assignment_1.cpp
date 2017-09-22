#define _CRT_SECURE_NO_WARNINGS
#define _SCL_SECURE_NO_WARNINGS

#define TRUE 1
#define FALSE 0

#include <iostream>
#include <stdlib.h>
#include <list>
#include <string>
#include <set>
#include <fstream>
#include <algorithm>
#include <vector>
#include <map>
#include <iomanip>

/*global variables*/
using namespace std;
set<int> item;
set<int> transaction;
set< set<int> > frequent_item_set;
map<set<int>, float> frequent_item_set_support;
multiset< set<int> > all_transaction;
int num_of_transaction = 0;
float min_sup;
FILE *file;

/*functions*/
void find_frequent_item_set(set< set<int> > item_set);
//bool check_set_include(set<int> set_a, set<int> set_b);
bool prunning(set<int> item_set);
int calculate_support(set<int> item_set);
void split_input_string(char * _input_string);
set< set<int> > cut_smaller_than_support_set(set< set<int> > item_set);
set< set<int> > make_next_candidate_set(set< set<int> > item_set);
void make_rules(set<int> first_set, set<int> second_set);
int* check_set_k_1_same(set<int> set_a, set<int> set_b);

/*main function*/
int main(int argc, char **argv) {
	char _input_string[200];
	ifstream read_file;
	int temp_set_size;
	set<int> temp_set;
	set<int>::iterator item_iterator;
	set< set<int> >::iterator frequent_item_set_iterator;

	read_file.open(argv[2]);
	min_sup = (float)atoi(argv[1])/100.0;
	while(!read_file.eof()) {
		read_file.getline(_input_string, 200);
		/*get input like string, go to split strings. it operate like string tokenizer*/
		split_input_string(_input_string);
		num_of_transaction++;
	}
	//inputs are done. we have all transaction set and set of items that used in transaction
	
	for (item_iterator = item.begin(); item_iterator != item.end(); item_iterator++) {
		temp_set.insert(*item_iterator);
		frequent_item_set.insert(temp_set);
		temp_set.clear();
	}
	read_file.close();
	//start Apriori algorithm
	printf("Start Apriori!\n");
	frequent_item_set = cut_smaller_than_support_set(frequent_item_set);
	find_frequent_item_set(frequent_item_set);
	//end Apriori algorithm
	
	set<int> first_set;
	file = fopen(argv[3], "w");
	printf("Now print...\n");
	
	//find Association rules
	for (frequent_item_set_iterator = frequent_item_set.begin(); frequent_item_set_iterator != frequent_item_set.end(); frequent_item_set_iterator++) {
		temp_set = (*frequent_item_set_iterator);
		if (temp_set.size() == 1)
			continue;
		temp_set_size = temp_set.size();
		make_rules(first_set, temp_set);
		
	}

	return 0;
}

/*receive input data using string, let`s the string makes some set of integer*/
void split_input_string(char *_input_string) {
	set<int>::iterator item_iterator;
	string input_string;
	string split;
	int place_of_tap = 0, product_number;
	input_string.append(_input_string);

	/*string tokenizer*/
	while (place_of_tap != -1) {
		place_of_tap = input_string.find("\t");
		split = input_string.substr(0, place_of_tap);
		product_number = stoi(split);
		transaction.insert(product_number);
		item.insert(product_number);
		/*increase iterator*/
		input_string = input_string.substr(place_of_tap + 1);
	}
	/*add transactions to all trasaction sets*/
	all_transaction.insert(transaction);
	transaction.clear();
}

/*check one set includes the other set. check if a -> b or not*/
/*bool check_set_include(set<int> set_a, set<int> set_b) {
	set<int>::iterator set_iterator_a;
	set<int>::iterator set_iterator_b;
	int item_a, item_b;
	if (set_a.size() > set_b.size())
		return false;
	set_iterator_a = set_a.begin();
	set_iterator_b = set_b.begin();

	while (set_iterator_b != set_b.end()) {
		if ((*set_iterator_a) == (*set_iterator_b)) {
			set_iterator_a++;
			set_iterator_b++;
		}
		else if ((*set_iterator_a) < (*set_iterator_b))
			break;
		else
			set_iterator_b++;

		if (set_iterator_a == set_a.end())
			return true;
	}
	return false;
}*/
// this function replaced by "includes"

//function for check two sets if they have same k-1 of elements 
int* check_set_k_1_same(set<int> set_a, set<int> set_b) {
	set<int>::iterator set_iterator_a = set_a.begin();
	set<int>::iterator set_iterator_b = set_b.begin();
	static int ret[3];
	int number = 0;
	
	//check start
	while (set_iterator_b != set_b.end()) {
		// if two sets have same elements increase iterators
		if ((*set_iterator_a) == (*set_iterator_b)) {
			number++;
			set_iterator_a++;
			set_iterator_b++;
		}
		/* if set a is smaller than set b, increase iterator of a and save the element
		 this can cover case {0, 1, 2}, {1, 2, 3} when two iterators point first element
		 then, saving 0 of set a and increase iterator of a.
		*/
		else if ((*set_iterator_a) < (*set_iterator_b)) {
			ret[2] = (*set_iterator_a);
			set_iterator_a++;
		}
		/*if set b is smaller than set a, increase iterator of b and save the element
		this can cover case {0, 1, 3, 4} {0, 1, 2, 3} when iterator direct 3 of a 2 of b. 
		*/
		else {
			ret[1] = (*set_iterator_b);
			set_iterator_b++;
		}
		if (set_iterator_a == set_a.end() && set_iterator_b != set_b.end()) {
			ret[1] = (*set_iterator_b);
			break;
		}
	}
	/*if k-1 is same return true*/
	if (number + 1 == set_a.size()) {
		ret[0] = TRUE;
		return ret;
	}
	else {
		ret[0] = FALSE;
		return ret;
	}
}

//function for cut the set that is smaller than min support
set< set<int> > cut_smaller_than_support_set(set< set<int> > item_set) {
	set< set<int> >::iterator item_set_iterator;
	set< set<int> > temp_set;
	set<int> to_erase_set;
	temp_set = item_set;
	float result;
	printf("Running...(survive support > min_sup)\n");
	/*iterate all candidiate set and cut if support of the set were smaller than min support*/
	for (item_set_iterator = item_set.begin(); item_set_iterator != item_set.end(); item_set_iterator++) {
		result = (float)calculate_support(*item_set_iterator) / (float)num_of_transaction;
		if (result < min_sup) {
			to_erase_set = *item_set_iterator;
			temp_set.erase(to_erase_set);
		}
		else {
			/* write set and the set`s support. it will be use make association rules*/
			frequent_item_set_support.insert(pair< set<int>, float>((*item_set_iterator), result));
		}
	}

	return temp_set;
}

//function for calculate support
int calculate_support(set<int> item_set) {
	multiset< set<int> >::iterator multiset_iterator;
	int support = 0;
	/*iterating all transaction, calculate support of item_set*/
	for (multiset_iterator = all_transaction.begin(); multiset_iterator != all_transaction.end(); multiset_iterator++) {
		if (item_set.size() > (*multiset_iterator).size())
			continue;
		//use includes function that is implemented in <algorithm>
		if (includes((*multiset_iterator).begin(), (*multiset_iterator).end(), item_set.begin(), item_set.end())) {
			support++;
		}
	}
	return support;
}

//function for make next level of candidate set
set< set<int> > make_next_candidate_set(set< set<int> > item_set) {
	set< set<int> > return_set;
	set< set<int> >::iterator item_set_iterator1;
	set< set<int> >::iterator item_set_iterator2;
	set<int>::iterator item_iterator1;
	set<int>::iterator item_iterator2;
	set<int> temp_set;
	int* flag;
	bool result_of_prunning;
	printf("Running...(make candidate set)\n");

	/*iterate all item set*/
	for (item_set_iterator1 = item_set.begin(); item_set_iterator1 != item_set.end(); item_set_iterator1++) {
		temp_set = *item_set_iterator1;
		/*iterate all item set*/
		for (item_set_iterator2 = item_set_iterator1; item_set_iterator2 != item_set.end(); item_set_iterator2++) {
			if (item_set_iterator1 == item_set_iterator2)
				continue;
			/*if two set`s elements k-1 same, than make candidate set*/
			flag = check_set_k_1_same(temp_set, *item_set_iterator2);
			if (flag[0] == FALSE) {
				continue;
			}
			else {
				temp_set.insert(flag[1]); /*here, we make candidate set*/
				result_of_prunning = prunning(temp_set);/*check all subsets are frequent or not*/
				if(result_of_prunning)
					return_set.insert(temp_set);/*if all subsets are frequent too, insert in return set*/
				temp_set.erase(flag[1]);
			}
		}
	}
	return return_set;
}

//function for cut the set that can`t satisfy apriori property
//Apriori property (if a set is frequent set, all subsets are frequent too )
bool prunning(set<int> item_set) {
	set<int> temp = item_set;
	set<int> real = temp;
	set<int>::iterator set_iterator;
	int saving;
	/*find item_set`s subsets are frequent*/
	for (set_iterator = temp.begin(); set_iterator != temp.end(); set_iterator++) {
		saving = *set_iterator;
		real.erase(saving);
		if (frequent_item_set.find(real) == frequent_item_set.end()) {
			return false;
		}
		real.insert(saving);
	}
	return true;
}

/*find frequent item set*/
void find_frequent_item_set(set< set<int> > item_set) {
	set< set<int> > temp_set = item_set;
	set< set<int> >::iterator item_set_iterator;
	/*find frequent item set*/
	while(!temp_set.empty()) {
		temp_set = make_next_candidate_set(temp_set);
		temp_set = cut_smaller_than_support_set(temp_set);
		/*In this step, temp_set have frequent item set*/
		for (item_set_iterator = temp_set.begin(); item_set_iterator != temp_set.end(); item_set_iterator++) {
			frequent_item_set.insert(*item_set_iterator);
		}
	}	
}

/*function for printing in file*/
void print(set<int> set_a, set<int> set_b) {
	set<int>::iterator set_a_iterator, set_b_iterator;
	string buffer;
	const char *cbuffer;
	int last_index;
	float support, confidence;
	buffer = "{";
	for (set_a_iterator = set_a.begin(); set_a_iterator != set_a.end(); set_a_iterator++) {
		buffer += to_string(*set_a_iterator);
		buffer += ",";
	}
	last_index = buffer.find_last_of(",");
	buffer = buffer.substr(0, last_index);
	buffer += "}\t";
	buffer += "{";
	for (set_b_iterator = set_b.begin(); set_b_iterator != set_b.end(); set_b_iterator++) {
		buffer += to_string(*set_b_iterator);
		buffer += ",";
	}
	last_index = buffer.find_last_of(",");
	buffer = buffer.substr(0, last_index);
	buffer += "}\t";
	cbuffer = buffer.c_str();
	fprintf_s(file, "%s", cbuffer);
	buffer.clear();

	vector<int> temp_union;
	temp_union.resize(set_a.size() + set_b.size());
	auto itr = set_union(set_a.begin(), set_a.end(), set_b.begin(), set_b.end(), temp_union.begin());
	temp_union.erase(itr, temp_union.end());
	set<int> result(temp_union.begin(), temp_union.end());
	
	support = frequent_item_set_support.find(result)->second * 100;
	confidence = (support / frequent_item_set_support.find(set_a)->second);
	fprintf_s(file, "%.2f\t%.2f\n", support, confidence);
}

/*function for make association rules*/
void make_rules(set<int> first_set, set<int> second_set) {
	set<int> set_a, set_b;
	set<int>::iterator set_iterator, set_checker;
	set<set<int> > ret;
	set_a = first_set;
	set_b = second_set;
	if (set_b.size() == 1)
		return ;
	
	if (!set_a.empty()) {
		set_checker = set_a.begin();
	}
	/*make rules by using recursive function*/
	for (set_iterator = second_set.begin(); set_iterator != second_set.end(); set_iterator++) {
		if (!set_a.empty() && *set_checker < *set_iterator)
			break;
		set_a.insert(*set_iterator);
		set_b.erase(*set_iterator);
		print(set_a, set_b);
		/*recursivly call
		* example
		* if {0, 1, 2} were the set we want to find association rules, 
		* this function can find result following these sequence.
		* {0}, {1,2}
		* {0, 1} {2}
		* {0, 2} {1}
		* {1} {0,2}
		* {1. 2} {0}
		* {2} {0, 1}
		*/
		make_rules(set_a, set_b);
		set_a.erase(*set_iterator);
		set_b.insert(*set_iterator);
	}
}
