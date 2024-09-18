from scripts.db_util import fetch_db_rows_as_dicts, fetchTopologies
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv, dotenv_values 
import pandas as pd
import math
import random

load_dotenv()

demographicsDict ={
    'CharlesTown': {
        'demographic':'CharlesTown city people are Living for today people mostly with a population of 10000. Out of this 65% are between the age of 18-25.',
        'population': 10000},
    'Limburg': {'demographic':'Limburg city people are young families people mostly with a population of 20000. Out of this 65% are between the age of 30-45. Most of them have kids aged between 0-15',
                'population': 20000}
}

banks = ['Culture', 'Fortune', 'Tornado']

GOOGLE_API_KEY= os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name = "gemini-pro")
DB_LOCATION = 'data.sqlite'


def get_random_bank():
    return random.choice(banks)
   

def load_json_from_string(json_string):
    try:
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def concatenate_keys(keys):
    concatenated_string = ""
    for i, d in enumerate(keys, start=1):
        concatenated_string += f"{i}. {d}"
    print('##########################')
    print(concatenated_string.strip())
    return concatenated_string.strip()

def transform_to_dict_of_dicts(columns, rows):
    # Initialize the result dictionary
    result = {}

    # Iterate over each row
    for row in rows:
        #print(dict(row))
        # The first element of the row is the key for the outer dictionary
        outer_key = row[0].strip()
        
        # Initialize the inner dictionary
        inner_dict = {}
        
        # Iterate over the rest of the elements in the row
        for i, value in enumerate(row[1:], start=1):
            # The corresponding column name is the key for the inner dictionary
            inner_key = columns[i].strip()
            # Add the key-value pair to the inner dictionary
            inner_dict[inner_key] = value
        
        # Add the inner dictionary to the result dictionary with the outer key
        result[outer_key] = inner_dict

    return result


def transform_topologies_to_dict(columns, rows):
    # Initialize the result dictionary
    result = {}

    # Iterate over each row
    for row in rows:
        #print(dict(row))
        # The first element of the row is the key for the outer dictionary
        outer_key = row[0].strip()
        
        # Initialize the inner dictionary
        inner_dict = {}
        
        # Iterate over the rest of the elements in the row
        for i, value in enumerate(row[1:], start=1):
            # The corresponding column name is the key for the inner dictionary
            inner_key = columns[i].strip()
            # Add the key-value pair to the inner dictionary
            inner_dict[inner_key] = value
        
        # Add the inner dictionary to the result dictionary with the outer key
        result[outer_key] = inner_dict

    return result

def listNeeds(tableName, dbName=DB_LOCATION):
    needs, rows = fetch_db_rows_as_dicts(dbName, tableName)
    needsDict = transform_to_dict_of_dicts(needs, rows)
    return list(needsDict.keys()), needsDict

def findTop3MoneyNeeds(proposition):
    moneyNeeds, rows = fetch_db_rows_as_dicts(DB_LOCATION, 'money_needs')
    moneyNeedsDict = transform_to_dict_of_dicts(moneyNeeds, rows)
    #print(list(moneyNeedsDict.keys()))
    needs = findTop3Needs(proposition, list(moneyNeedsDict.keys()))
    needDictIndexes = []
    for need in needs:
        needDictIndexes.append(moneyNeedsDict[need])

    #print(needDictIndexes)
    return needs, needDictIndexes

def findTop3CustomerExperienceNeeds(proposition):
    moneyNeeds, rows = fetch_db_rows_as_dicts(DB_LOCATION, 'customer_exp')
    moneyNeedsDict = transform_to_dict_of_dicts(moneyNeeds, rows)
    #print(list(moneyNeedsDict.keys()))
    needs = findTop3Needs(proposition, list(moneyNeedsDict.keys()))
    needDictIndexes = []
    for need in needs:
        needDictIndexes.append(moneyNeedsDict[need])

    #print(needDictIndexes)
    return needs, needDictIndexes


def findTop3SustainabilityNeeds(proposition):
    print(" Proposition sustain  = {}".format(proposition))
    allNeeds, rows = fetch_db_rows_as_dicts(DB_LOCATION, 'sustainability')
    needsDict = transform_to_dict_of_dicts(allNeeds, rows)
    
    needs = findTop3Needs(proposition, list(needsDict.keys()))
    needDictIndexes = []
    print(list(needsDict.keys()))
    for need in needs:
        needDictIndexes.append(needsDict[need])

    print(needDictIndexes)
    return needs, needDictIndexes


def findTop3Needs(proposition, needs):
    
    needsString = concatenate_keys(needs)

    prompt = '''You have this comma separated listed needs of customers
    {}

    Now given a proposition 
    "{}" 
    
    Find the best 3 strings out of the above numbered list which best matches this proposition. Return in output only the number next to the matching string strictly only in json under a list called matches
    '''

    needsPrompt = prompt.format(needsString, proposition)
    print(needsPrompt)
    response = model.generate_content([needsPrompt])
    output = response.text
    output = output.replace('```json', '')
    output = output.replace('```', '')
    obj = load_json_from_string(output)
    print(obj)

    needsIndexes = [needs[int(idx)-1] for idx in obj['matches']]
    return needsIndexes #obj['matches']


def findTop3Topologies(proposition, demographic):

    topologies = fetchTopologies()

    topologies = topologies.dropna(axis=1, how='all')
    
    topologyAttributes = topologies['Column1']
    topologyNames = list(topologies.columns)
    topologyNames.remove('Column1')

    #print(" topologyNames = {} ", topologyNames)
    
    topologyDetails = {}

    for name in topologyNames:
        topologyDetails[name] = {}
        for attribute in topologyAttributes:
            topologyDetails[name][attribute] = topologies[name][pd.Index(topologies['Column1']).get_loc(attribute)]
            
    prompt = '''You have these listed topology names of a demographic in comma separated values below
    {}

    Now for each of these above topologies here are the details
    {}

    Now given a proposition details below
    
    {}

    and given a demographic details below

    {}
    
    Find the best 3 common strings out of the topology names which matches the proposition and the demographic the most. Return output strictly only in json under a list called matches
    '''

    topologyPrompt = prompt.format(", ".join(topologyNames), str(topologyDetails), proposition, demographic)
    response = model.generate_content([topologyPrompt])
    output = response.text
    output = output.replace('```json', '')
    output = output.replace('```', '')
    obj = load_json_from_string(output)
    print(obj)
    return obj['matches'], topologyDetails


def generatePropositionExample(productName, selectedProduct, moneyNeeds, customerExperience, sutainabilityNeeds):

    proposal = '''You are a business sales professional who can form propostion summary of 100 words based upon the details.
    Please take the below details and summarize a propostion in less than 100 words.

    product name = {}
    
    product type = {}

    money needs of customer which this product is supposed to target = {}

    Customer experience needs which our company will provide = {}

    Sustainability needs which our product takes care of = {}
    '''
    proposal = proposal.format(productName, selectedProduct, moneyNeeds, customerExperience, sutainabilityNeeds)
    response = model.generate_content([proposal])
    return response.text


def evaluateProposition(selectedCity, selectedProduct, userProposal, moneyNeeds, customerExpNeeds, sustainabilityNeeds):
    
    proposal = '''Given proposal is for the city {} with product {}. The propsal is as below.
    {}'''
    proposal = proposal.format(selectedCity, selectedProduct, userProposal)

    _, moneyNeedsDict = listNeeds('money_needs')
    _, customerExperienceDict = listNeeds('customer_exp')
    _, sutainabilityNeedsDict = listNeeds('sustainability')

    demographic = demographicsDict[selectedCity]['demographic']
    population = demographicsDict[selectedCity]['population']
    matchingTopologies, topologyDetails = findTop3Topologies(proposal, demographic)
   
    topologySumDict = {}

    for topology in matchingTopologies:
        sumTopology = 0
        for moneyNeed in moneyNeeds:
            print(" Money need = {}, Topology is {}".format(moneyNeed, topology))
            sumTopology = sumTopology+int(moneyNeedsDict[moneyNeed][topology])
        
        for customerExp in customerExpNeeds:
            sumTopology = sumTopology+int(customerExperienceDict[customerExp][topology])

        for sustainabilityNeed in sustainabilityNeeds:
            sumTopology = sumTopology+int(sutainabilityNeedsDict[sustainabilityNeed][topology])

        topologySumDict[topology] = math.floor(sumTopology/3)

    totalSubscriberTakeOut = 0
    for topology in matchingTopologies:
        proportion = int(topologyDetails[topology]['Proportion Sample'].replace('%', ''))
        topologyPopulation = math.floor((proportion * population) / 100)

        topologyScore = topologySumDict[topology]

        topologyPopulation = math.floor(topologyPopulation/2)
        if topologyScore <=250:
            topologyPopulation = topologyPopulation/2

        elif topologyScore >250 and topologyScore<=260:
            topologyPopulation = math.floor(topologyPopulation/1.8)
        
        elif topologyScore >260 and topologyScore<=270:
            topologyPopulation = math.floor(topologyPopulation/1.6)

        elif topologyScore >270 and topologyScore<=280:
            topologyPopulation = math.floor(topologyPopulation/1.4)

        elif topologyScore >280 and topologyScore<=300:
            topologyPopulation = topologyPopulation
        
        elif topologyScore >300 and topologyScore<=310:
            topologyPopulation = math.floor(topologyPopulation * 1.2)

        elif topologyScore >310 and topologyScore<=320:
            topologyPopulation = math.floor(topologyPopulation * 1.4)
        
        elif topologyScore >320 and topologyScore<=340:
            topologyPopulation = math.floor(topologyPopulation * 1.5)
        
        elif topologyScore >340 and topologyScore<=360:
            topologyPopulation = math.floor(topologyPopulation * 1.6)
        
        else:
             topologyPopulation = math.floor(topologyPopulation * 2)

        totalSubscriberTakeOut = totalSubscriberTakeOut + topologyPopulation
    
    return matchingTopologies, totalSubscriberTakeOut 
#        st.write("{}. {} and has subscriber takeout of {}".format(topology, topologySumDict[topology], topologyPopulation))

#    st.write(" Target Subscriber takeout = {}".format(totalSubscriberTakeOut))
#    st.write(" Total Subscriber take up for Year 3 = {}".format(subscriberTakeOutYear3))

#    if totalSubscriberTakeOut<subscriberTakeOutYear3:
#        st.write("Overall there is not a close match of your proposition to the main demographic. Takeout score difference = {}".format(subscriberTakeOutYear3-totalSubscriberTakeOut))
#    elif totalSubscriberTakeOut==subscriberTakeOutYear3:
#        st.write("Amazing! Your proposition  exactly match the target subscriber take oup for year 3")
#    else:
#        st.write("Great Job! Your proposition exceeds the target subscriber take up for year 3. Additional takeout = {}".format(totalSubscriberTakeOut- subscriberTakeOutYear3))
