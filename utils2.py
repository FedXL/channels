def string_to_list(string):
    return list(map(int, string.strip('[]').split(',')))

def turn_1_to_0001(channel):
    len_channel = len(str(channel))
    zero = 4 - len_channel
    channel = "0" * zero + str(channel)
    return channel

