# test if round half up works for negative decimals

import converter, math

init_num = 7.5
print('init_num: ' + str(init_num))

# int_num = math.ceil(init_num)
# print('int_num: ' + str(int_num))

# # fractions do not work
# # but negatives do
# # num_round_digits = 0.5
# # print('num_round_digits: ' + str(num_round_digits))

# # round_num = converter.round_half_up(init_num, num_round_digits)
# # print('round_num: ' + str(round_num))

# def round_to_base(x, base=5):
#     return base * round(x/base)

def round_to_base(x, base=5):
    return base * converter.round_half_up(x/base)

# cant have base 0 bc divide by 0
# if init num < 5, round up to 5
if init_num < 5:
    init_num = 5

base = 5
print('base: ' + str(base))
round_num = round_to_base(init_num, base)
print('round_num: ' + str(round_num))