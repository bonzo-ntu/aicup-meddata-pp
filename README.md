# Environments
* OS: `ubuntu 20.0.4`  
* GPU: 
    ```bash
       product: TU104GL [Tesla T4]
       vendor: NVIDIA Corporation
       driver version: 510.47.03
       CUDA Version: 11.6 
       width: 64 bits
       clock: 33MHz
    ```  
* Python version: `Python 3.10.13`  

# How to setup
```bash
# install python3.10
sudo add-apt-repository ppa:deadsnakes/ppa
yes | sudo apt install python3.10

# install packages
pip install -r requirements.txt
```

# How to run
```bash
# to generate finetune jsonl file
python data_preprocess_openai.py
```
then execute `finetune_openai.ipynb` by the instruction
remember to create your OpenAI account and get the OpenAI api key before you run the `finetune_openai.ipynb`  
**note**: since our OpenAI key cannot be revealed in public, the `finetune_openai.ipynb` may not work for you because  
      the finetuned model is not accessible in a different OpenAI account  

# How to run (our failuir ex)
```bash
# PEFT train 10 epochs and print eval results
python train_lora.py
```
