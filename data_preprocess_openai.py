# %%
import os
os.chdir('/home/jupyter/aicup-meddata-pp')

# %%
import tiktoken
import pandas as pd

# %%
def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# %%
def find_context(df, valid=False):
    source_folder_dict = {1:'./content/First_Phase_Release/First_Phase_Text_Dataset', 
                          2:'./content/Second_Phase_Dataset/Second_Phase_Text_Dataset',
                          3:'./content/opendid_test/', 
                          4:'./content/First_Phase_Release/Validation_Release'} 
    
    current_file = ''
    
    context = []
    for id, row in df.iterrows():
        
        file, start_id, sentence =  row.file, row.start_id, row.sentence
        if not valid:
            source =  row.source
            record_path = source_folder_dict[source]
        else:
            record_path = './content/First_Phase_Release/Validation_Release'
        new_file = f'{record_path}/{file}.txt'
        if current_file != new_file:
            #print(f'new file:{new_file} opened')
            current_file = new_file
            record = open(current_file, 'r').read()

        s = 0 if start_id - 100 <= 0 else start_id - 100
        e = start_id + len(sentence) + 100
        context.append(record[s:e])


    return context

# %%
train = pd.read_csv('./train_pp.tsv', delimiter='\t')
valid = pd.read_csv('./valid_pp.tsv', delimiter='\t')
test = pd.read_csv('./test_pp.tsv', delimiter='\t')

train['sentence'] = train.sentence.fillna('')
valid['sentence'] = valid.sentence.fillna('')
test['sentence'] = test.sentence.fillna('')

train['context'] = find_context(train)
valid['context'] = find_context(valid)
test['context'] = find_context(test)

train.to_csv('./train_pp_context.tsv', index=False, sep='\t')
valid.to_csv('./valid_pp_context.tsv', index=False, sep='\t')
test.to_csv('./test_pp_context.tsv', index=False, sep='\t')

# %%
def get_phis(s):
    return [section.split(':')[0] for section in s.split('\\n') if section.split(':')[0]]

def gen_ft_df(start = 0, n = 20, skip_low=False, threshold=136):
    df = pd.read_csv('./train_pp_context.tsv', delimiter='\t')

    phis = "PATIENT, DOCTOR, DEPARTMENT, HOSPITAL, STREET, CITY, STATE, ZIP, DATE, TIME, MEDICALRECORD, IDNUM, PHI".split(',')
    phis = [_.replace(' ','') for _ in phis]

    train_df_data, train_df_meta = {}, {}
    for phi in phis:
        result = df[df.label.apply(lambda x: phi in get_phis(x))].copy()
        if result.shape[0] > 0:
            train_df_data[phi] = result
            train_df_meta[phi] = result.shape[0]
        else:
            print(f'{phi} skipped')
    

    dfs = []
    for phi in phis:
        if train_df_meta[phi] < threshold:
            if not skip_low:
                dfs.append(train_df_data[phi])
        else:
            tmp = train_df_data[phi]
            tmp1 = tmp[tmp.source == 1].iloc[start:start+n//2, :]
            tmp2 = tmp[tmp.source == 2].iloc[start:start+n//2, :]
            dfs.append(tmp1)
            dfs.append(tmp2)

    ft_df = pd.concat(dfs, axis=0).reset_index(drop=True).drop_duplicates()
    return ft_df


# def gen_ft_df3(n = 20):
#     df = pd.read_csv('./train_pp.tsv', delimiter='\t')

#     #phis = "PATIENT, DOCTOR, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, AGE, DATE, TIME, MEDICALRECORD, IDNUM, PHI:Null".split(',')
#     phis = "PATIENT, DOCTOR, DEPARTMENT, HOSPITAL, STREET, CITY, STATE, ZIP, DATE, TIME, MEDICALRECORD, IDNUM, PHI".split(',')
#     phis = [_.replace(' ','') for _ in phis]

#     train_df_data, train_df_meta = {}, {}
#     for phi in phis:
#         result = df[df.label.apply(lambda x: phi in get_phis(x))].copy()
#         if result.shape[0] > 0:
#             train_df_data[phi] = result
#             train_df_meta[phi] = result.shape[0]
#         else:
#             print(f'{phi} skipped')
    

#     dfs = []
#     for phi in phis:
#         if train_df_meta[phi] < n:
#             dfs.append(train_df_data[phi])

#     ft_df = pd.concat(dfs, axis=0).reset_index(drop=True).drop_duplicates()
#     return ft_df


# %%
import pandas as pd
import json
def gen_ft_file(df, filename, prompt_type = 3):
    source_folder_dict = {1:'./content/First_Phase_Release/First_Phase_Text_Dataset', 
                          2:'./content/Second_Phase_Dataset/Second_Phase_Text_Dataset',
                          3:'./content/opendid_test/', 
                          4:'./content/First_Phase_Release/Validation_Release'} 
    
    with open(filename, 'w') as jsonl_file:
        for row in df.iterrows():
            id, row = row

            role = "You are a doctor, capable of identifying Protected Health Information (PHI) within medical records."

            source, file, sentence, label =  row.source, row.file, row.sentence, row.label
            record_path = source_folder_dict[source]

            if prompt_type == 1: 
                record = open(f'{record_path}/{file}.txt', 'r').read()

                phis = "PATIENT, DOCTOR, ROOM, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, LOCATION-OTHER, AGE, DATE, TIME, DURATION, SET, PHONE, URL, MEDICALRECORD, IDNUM"
                rule = f"PHI categories are: {phis}. If the content can not be identified as any of PHI category, reply a special string 'PHI:Null'"
                user_input = f"Please read the medical record: ```\n{record}\n``` and identify all PHI categories in the the sentence: ```\n{sentence}\n```. Respond in the format 'PHI Category: PHI Content' for each identified PHI category. If there are multiple PHI categories in the sentence, separate all 'PHI Category: PHI Content' pairs with '\n'."
            elif prompt_type == 2:
                record = row.context

                phis = "PATIENT, DOCTOR, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, AGE, DATE, TIME, MEDICALRECORD, IDNUM"
                rule = f"PHI categories are: {phis}. If the content can not be identified as any of PHI category, reply a special string 'PHI:Null'"
                user_input = f"Please read the medical record paragraph: ```\n{record}\n``` and identify all PHI categories in this sentence: ```\n{sentence}\n```. Respond in the format 'PHI Category: PHI Content' for each identified PHI category. If there are multiple PHI categories in the sentence, separate all 'PHI Category: PHI Content' pairs with '\n'."
            elif prompt_type == 3:
                phis = "PATIENT, DOCTOR, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, AGE, DATE, TIME, MEDICALRECORD, IDNUM"
                rule = f"PHI categories are: {phis}. If the content can not be identified as any of PHI category, reply a special string 'PHI:Null'"
                user_input = f"Please identify all PHI categories in this sentence (from a medical record): ```\n{sentence}\n```. Respond in the format 'PHI Category:PHI Content' for each identified PHI category. If multiple PHI categories are identified, concatenate 'PHI Category:PHI Content' pairs with '\n'."


            ft_sample = [
                {"role": "system", "content": role},
                {"role": "assistant", "content": rule},
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": label}
            ]

            item = {"messages":ft_sample}    
            jsonl_file.write(json.dumps(item, ensure_ascii=False) + "\n")


def gen_ft_file2(df, filename):
    source_folder_dict = {1:'./content/First_Phase_Release/First_Phase_Text_Dataset', 
                          2:'./content/Second_Phase_Dataset/Second_Phase_Text_Dataset',
                          3:'./content/opendid_test/', 
                          4:'./content/First_Phase_Release/Validation_Release'} 
    with open(filename, 'w') as jsonl_file:
        for row in df.iterrows():
            id, row = row


            source, file, sentence, label =  row.source, row.file, row.sentence, row.label
            record_path = source_folder_dict[source]
            record = row.context

            role = "You are a doctor, capable of identifying Protected Health Information (PHI) within medical records."
            # phis = "PATIENT, DOCTOR, USERNAME, PROFESSION, ROOM, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, LOCATION-OTHER, AGE, DATE, TIME, DURATION, SET, PHONE, FAX, EMAIL, URL, IPADDR, SSN, MEDICALRECORD, HEALTHPLAN, ACCOUNT, LICENSE, VEHICLE, DEVICE, BIOID, IDNUM"
            phis = "PATIENT, DOCTOR, ROOM, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, LOCATION-OTHER, AGE, DATE, TIME, DURATION, SET, PHONE, URL, MEDICALRECORD, IDNUM"
            phis = "PATIENT, DOCTOR, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, AGE, DATE, TIME, MEDICALRECORD, IDNUM"
            rule = f"PHI categories are: {phis}. If the content can not be identified as any of PHI category, reply a special string 'PHI:Null'"
            user_input = f"Please read the medical record paragraph: ```\n{record}\n``` and identify all PHI categories in this sentence: ```\n{sentence}\n```. Respond in the format 'PHI Category: PHI Content' for each identified PHI category. If there are multiple PHI categories in the sentence, separate all 'PHI Category: PHI Content' pairs with '\n'."

            ft_sample = [
                {"role": "system", "content": role},
                {"role": "assistant", "content": rule},
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": label}
            ]

            item = {"messages":ft_sample}    
            jsonl_file.write(json.dumps(item, ensure_ascii=False) + "\n")


def gen_ft_file3(df, filename):
    source_folder_dict = {1:'./content/First_Phase_Release/First_Phase_Text_Dataset', 
                          2:'./content/Second_Phase_Dataset/Second_Phase_Text_Dataset',
                          3:'./content/opendid_test/', 
                          4:'./content/First_Phase_Release/Validation_Release'} 
    
    with open(filename, 'w') as jsonl_file:
        for row in df.iterrows():
            id, row = row

            source, file, sentence, label =  row.source, row.file, row.sentence, row.label
            record_path = source_folder_dict[source]
            record = row.context

            role = "You are a doctor, capable of identifying Protected Health Information (PHI) within medical records."
            # phis = "PATIENT, DOCTOR, USERNAME, PROFESSION, ROOM, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, LOCATION-OTHER, AGE, DATE, TIME, DURATION, SET, PHONE, FAX, EMAIL, URL, IPADDR, SSN, MEDICALRECORD, HEALTHPLAN, ACCOUNT, LICENSE, VEHICLE, DEVICE, BIOID, IDNUM"
            # phis = "PATIENT, DOCTOR, ROOM, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, LOCATION-OTHER, AGE, DATE, TIME, DURATION, SET, PHONE, URL, MEDICALRECORD, IDNUM"
            phis = "PATIENT, DOCTOR, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, AGE, DATE, TIME, MEDICALRECORD, IDNUM"
            rule = f"PHI categories are: {phis}. If the content can not be identified as any of PHI category, reply a special string 'PHI:Null'"
            user_input = f"Please identify all PHI categories in this sentence (from a medical record): ```\n{sentence}\n```. Respond in the format 'PHI Category: PHI Content' for each identified PHI category. If there are multiple PHI categories in the sentence, separate all 'PHI Category: PHI Content' pairs with '\n'."

            ft_sample = [
                {"role": "system", "content": role},
                {"role": "assistant", "content": rule},
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": label}
            ]

            item = {"messages":ft_sample}    
            jsonl_file.write(json.dumps(item, ensure_ascii=False) + "\n")


def gen_ft_file4(df, filename):
    source_folder_dict = {1:'./content/First_Phase_Release/First_Phase_Text_Dataset', 
                          2:'./content/Second_Phase_Dataset/Second_Phase_Text_Dataset',
                          3:'./content/opendid_test/', 
                          4:'./content/First_Phase_Release/Validation_Release'} 
    
    with open(filename, 'w') as jsonl_file:
        for row in df.iterrows():
            id, row = row

            source, file, sentence, label =  row.source, row.file, row.sentence, row.label
            record_path = source_folder_dict[source]
            record = row.context

            role = "You are a doctor, capable of identifying Protected Health Information (PHI) within medical records."
            # phis = "PATIENT, DOCTOR, USERNAME, PROFESSION, ROOM, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, LOCATION-OTHER, AGE, DATE, TIME, DURATION, SET, PHONE, FAX, EMAIL, URL, IPADDR, SSN, MEDICALRECORD, HEALTHPLAN, ACCOUNT, LICENSE, VEHICLE, DEVICE, BIOID, IDNUM"
            # phis = "PATIENT, DOCTOR, ROOM, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, LOCATION-OTHER, AGE, DATE, TIME, DURATION, SET, PHONE, URL, MEDICALRECORD, IDNUM"
            phis = "PATIENT, DOCTOR, DEPARTMENT, HOSPITAL, ORGANIZATION, STREET, CITY, STATE, COUNTRY, ZIP, AGE, DATE, TIME, MEDICALRECORD, IDNUM"
            rule = f"PHI categories are: {phis}. If the content can not be identified as any of PHI category, reply a special string 'PHI:Null'"
            user_input = f"Please identify all PHI categories in this sentence (from a medical record): ```\n{sentence}\n```. Respond in the format 'PHI Category:PHI Content' for each identified PHI category. If multiple PHI categories are identified, concatenate 'PHI Category:PHI Content' pairs with '\n'."

            ft_sample = [
                {"role": "system", "content": role},
                {"role": "assistant", "content": rule},
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": label}
            ]

            item = {"messages":ft_sample}    
            jsonl_file.write(json.dumps(item, ensure_ascii=False) + "\n")


# %%
gen_ft_file(gen_ft_df(0, n=100, skip_low=False), 'prompt1.jsonl', prompt_type=1)
gen_ft_file(gen_ft_df(0, n=100, skip_low=True), 'prompt2.jsonl', prompt_type=2)
gen_ft_file(gen_ft_df(0, n=500, skip_low=True), 'prompt3.jsonl', prompt_type=3)


