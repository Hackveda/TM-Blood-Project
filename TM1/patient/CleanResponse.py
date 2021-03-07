import json
""" clean_response.py : Clean response according to valid definitions """
""" submodule for process.py """


__author__ = 'Aman Goyal'

# Cleaning operations
def remove_invalid_na_unit_response(responses:list):
    """
    takes the list of responses from process.py, and for the respons in which a single tag name 
    had multiple response with correct unit and unit value "NA", it will suppress response with "NA"
    """
    collected_responses = {}
    
    # separating responses bases on their tag name
    for response in responses:
        curr_name      = response['name']

        # if curr_name is already in collected_responses
        if collected_responses.get(curr_name) is not None:
            collected_responses[curr_name].append( response)
        # if name already exist in collected_responses
        else:
            collected_responses[ curr_name ] = [ response ]

    final_response_list = []
    for tagname in collected_responses:
        unit_set = set(response['Unit'] for response in collected_responses[tagname])
        

        # if there are more than one type of unit than keep only those response
        # which doesn't have NA
        if len(unit_set)>1: 
            final_response_list += [response for response in collected_responses[tagname] if response['Unit']!='NA']
        else:
            final_response_list += collected_responses[tagname]

    return final_response_list



def clean_response(response_dict : dict) -> dict:
    """
    cleans the input dict containing response, to return only those results that are valid

    definition of valid:
        len(str(name))>0
        len(str(value))>0
        len(str(ReadIndex))>0
        str(value) in str(ReadIndex)
        # str(unit) in str(ReadIndex)  not enforced

    possible improvements:
        definition can be improved with stricter restrictions, If unit can be empty or not

    """
    result = []
    response = response_dict['Response']['Result']
    for tag in response:
        name  = tag['name']
        value = tag['Value']
        unit =  tag['Unit']
        ReadIndex = tag['ReadIndex']
        TempSent = tag['TempSent']

        # ASSUMPTION
        # keys name, value, Read Index cannot be empty
        if (len(name)<=0 or len(value)<=0 or len(ReadIndex)<=0 ):
            continue # donot add present response to final result

        # ASSUMPTION
        # ReadIndex contains 'value' and 'Unit'
        # If readindex doesn't contain `Vlaue` and `Unit` then
        # ReadIndex is flawed
        if not (
            str(value) in ReadIndex 
            # and str(unit) in ReadIndex
        ):
            continue # donot add present respone to final result
        
        # if unit is anything except 'NA' and its not is ReadIndex
        # ReadIndex is flawed 
        if (not (unit == 'NA')) and (not (unit in ReadIndex)):
            continue

        # if all the checks passes, then present response is correct 
        # add it to the final result
        result.append(tag)

        # removing invalid na unit responses
        result = remove_invalid_na_unit_response(result)

    return result

if __name__=="__main__":
    # name = 'sanjeev_response'
    # with open(f'{name}.json', 'r') as readfile:
    #     data=  json.load(readfile)
    # response = clean_response(data)
    # with  open(f'clean_{name}.json', 'w') as writefile:
    #     json.dump(response, writefile)
    # # print(response)
    # li = [
    # {
    #     "name": "ABSOLUTE NEUTROPHIL COUNT",
    #     "Value": "1000",
    #     "Unit": "NA",
    #     "ReadIndex": "(anc) <1000 - markedly increased susceptibility of infectious diseases",
    #     "TempSent": "(anc) <1000 - markedly increased susceptibility of infectious diseases"
    # },
    # {
    #     "name": "ABSOLUTE NEUTROPHIL COUNT",
    #     "Value": "1649.20",
    #     "Unit": "/cu mm",
    #     "ReadIndex": "(blood, 1649.20 2000 - 7000 /cu mm",
    #     "TempSent": "(blood, 1649.20 2000 - 7000 /cu mm"
    # },
    # {
    #     "name": "ABSOLUTE NEUTROPHIL COUNT",
    #     "Value": "1000",
    #     "Unit": "NA",
    #     "ReadIndex": "(anc) <1000 - markedly increased susceptibility of infectious diseases",
    #     "TempSent": "(anc) <1000 - markedly increased susceptibility of infectious diseases"
    # },
    # {
    #     "name": "ABSOLUTE NEUTROPHIL COUNT",
    #     "Value": "1000",
    #     "Unit": "NA",
    #     "ReadIndex": "(anc) <1000 - markedly increased susceptibility of infectious diseases",
    #     "TempSent": "(anc) <1000 - markedly increased susceptibility of infectious diseases"
    # },
    # {
    #     "name": "COUNT",
    #     "Value": "1000",
    #     "Unit": "NA",
    #     "ReadIndex": "(anc) <1000 - markedly increased susceptibility of infectious diseases",
    #     "TempSent": "(anc) <1000 - markedly increased susceptibility of infectious diseases"
    # },
    # {
    #     "name": "COUNT",
    #     "Value": "1000",
    #     "Unit": "NA",
    #     "ReadIndex": "(anc) <1000 - markedly increased susceptibility of infectious diseases",
    #     "TempSent": "(anc) <1000 - markedly increased susceptibility of infectious diseases"
    # },
    # {
    #     "name": "COUNT",
    #     "Value": "1000",
    #     "Unit": "NA",
    #     "ReadIndex": "(anc) <1000 - markedly increased susceptibility of infectious diseases",
    #     "TempSent": "(anc) <1000 - markedly increased susceptibility of infectious diseases"
    # },
    # {
    #     "name": "COUNT",
    #     "Value": "1000",
    #     "Unit": "NA",
    #     "ReadIndex": "(anc) <1000 - markedly increased susceptibility of infectious diseases",
    #     "TempSent": "(anc) <1000 - markedly increased susceptibility of infectious diseases"
    # },
    # {
    #     "name": "COUNT",
    #     "Value": "1000",
    #     "Unit": "NA",
    #     "ReadIndex": "(anc) <1000 - markedly increased susceptibility of infectious diseases",
    #     "TempSent": "(anc) <1000 - markedly increased susceptibility of infectious diseases"
    # },
    # {
    #     "name": "COUNT",
    #     "Value": "1000",
    #     "Unit": "NA",
    #     "ReadIndex": "(anc) <1000 - markedly increased susceptibility of infectious diseases",
    #     "TempSent": "(anc) <1000 - markedly increased susceptibility of infectious diseases"
    # },

    # ]
    # collected_response = remove_invalid_na_unit_response(li)
    # print(collected_response)
    # for res in collected_response:
    #     print(res)
    pass