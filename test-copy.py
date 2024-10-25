# test if deepcopy needed
# dict needs deepcopy

import copy

init_dict = {'1': '1'}

final_dict = copy.deepcopy(init_dict)

final_dict['2'] = '2'

print('init_dict: ' + str(init_dict))
print('final_dict: ' + str(final_dict))