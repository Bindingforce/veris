#!/usr/bin/env python
"""
 AUTHOR: Gabriel Bassett
 DATE: 06-09-16
 DEPENDENCIES: <a list of modules requiring installation>
 

 DESCRIPTION:
 Meant to be imported.  Takes json records and adds rules for correlated enumerations.
 that may have been left out of the original source file.

 NOTES:
 <No Notes>

 ISSUES:
 <No Issues>

 TODO:
 <No TODO>

"""
# PRE-USER SETUP
import logging

########### NOT USER EDITABLE ABOVE THIS POINT #################


# USER VARIABLES
LOGLEVEL = logging.DEBUG
LOG = None

########### NOT USER EDITABLE BELOW THIS POINT #################


## IMPORTS
import argparse
import ConfigParser

## SETUP
__author__ = "Gabriel Bassett"


## FUNCTION DEFINITION
def addRules(incident, logger):

    "Takes in an incident and applies rules for internal consistency and consistency with previous incidents"
    if 'action' not in incident:
        incident['action'] = { "Unknown" : {} }

    # Malware always has an integrity attribute
    if 'malware' in incident['action']:
        if 'attribute' not in incident:
            logging.info("%s: Added attribute.integrity since malware was involved.",iid)
            incident['attribute'] = {}
        if 'integrity' not in incident['attribute']:
            logging.info("%s: Added integrity since it has a malware action.",iid)
            incident['attribute']['integrity'] = {}
        if 'variety' not in incident['attribute']['integrity']:
            logging.info("%s: Added integrity.variety array since it didn't have one.",iid)
            incident['attribute']['integrity']['variety'] = []
        if 'Software installation' not in incident['attribute']['integrity']['variety']:
            logging.info("%s: Added software installation to attribute.integrity.variety since malware was involved.",iid)
            incident['attribute']['integrity']['variety'].append('Software installation')

    # Social engineering alters human behavior
    if 'social' in incident['action']:
        if 'attribute' not in incident:
            logging.info("%s: Added attribute.integrity since social engineering was involved.",iid)
            incident['attribute'] = {}
            incident['attribute']['integrity'] = {}
        if 'integrity' not in incident['attribute']:
            logging.info("%s: Added attribute.integrity since social engineering was involved.",iid)
            incident['attribute']['integrity'] = {}
        if 'variety' not in incident['attribute']['integrity']:
            logging.info("%s: Added attribute.integrity.variety array since it wasn't there.",iid)
            incident['attribute']['integrity']['variety'] = []
        if 'Alter behavior' not in incident['attribute']['integrity']['variety']:
            logging.info("%s: Added alter behavior to attribute.integrity.variety since social engineering was involved.",iid)
            incident['attribute']['integrity']['variety'].append('Alter behavior')

    # The target of social engineering is one of the affected assets
    if 'social' in incident['action']:
        if 'target' not in incident['action']['social']:
            logging.info("%s: Added action.social.target since it wasn't there.",iid)
            incident['action']['social']['target'] = ['Unknown']
        if 'asset' not in incident:
            logging.info("%s: Added asset object since it wasn't there.",iid)
            incident['asset'] = {}
        if 'assets' not in incident['asset']:
            logging.info("%s: Added asset.assets list since it wasn't there.",iid)
            incident['asset']['assets'] = []
        asset_list = list()
        for each in incident['asset']['assets']:
            asset_list.append(each['variety'])
        for each in incident['action']['social']['target']:
            if each == "Unknown":
                if 'P - Other' not in asset_list:
                    logging.info("%s: Adding P - Other to asset list since there was social engineering.",iid)
                    incident['asset']['assets'].append({'variety':'P - Other'})
                    continue
            if 'P - '+each not in asset_list:
                if 'P - '+each != 'P - Unknown':
                    logging.info("%s: Adding P - %s to asset list since there was social engineering.",each,iid)
                    incident['asset']['assets'].append({'variety':'P - '+each})

    # If SQLi was involved then there needs to be misappropriation too
    if 'hacking' in incident['action']:
        if 'variety' not in incident['action']['hacking']:
            logging.info("%s: Adding hacking variety because it wasn't in there.",iid)
            incident['action']['hacking']['variety'] = ['Unknown']
        if 'SQLi' in incident['action']['hacking']['variety']:
            if 'integrity' not in incident['attribute']:
                logging.info("%s: Adding attribute.integrity since SQLi was involved.",iid)
                incident['attribute']['integrity'] = {'variety': [] }
            if 'variety' not in incident['attribute']['integrity']:
                logging.info("%s: Adding attribute.integrity.variety array since it was omitted.",iid)
                incident['attribute']['integrity']['variety'] = []
            if 'Repurpose' not in incident['attribute']['integrity']['variety']:
                logging.info("%s: Adding repurpose since SQLi was there.",iid)
                incident['attribute']['integrity']['variety'].append('Repurpose')

    # If there is a theft or loss then there is an availability loss
    if 'physical' in incident['action']:
        if 'Theft' in incident['action']['physical']['variety']:
            if 'availability' not in incident['attribute']:
                logging.info("%s: Added attribute.availability since there was theft.",iid)
                incident['attribute']['availability'] = {'variety': ['Loss']}
            if 'Loss' not in incident['attribute']['availability']['variety']:
                logging.info("%s: Added Loss to attribute.availability.variety in respone %s since there was theft.",iid)
                incident['attribute']['availability']['variety'].append('Loss')
    if 'error' in incident['action']:
        if 'Loss' in incident['action']['error']['variety']:
            if 'availability' not in incident['attribute']:
                logging.info("%s: Added attribute.availability since there was theft.",iid)
                incident['attribute']['availability'] = {'variety': ['Loss']}
            if 'Loss' not in incident['attribute']['availability']['variety']:
                logging.info("%s: Added Loss to attribute.availability.variety in respone %s since there was theft.",iid)
                incident['attribute']['availability']['variety'].append('Loss')

    # Commented out as discussion is these should only be applied to SG short form-entered incidents
    '''
    # ATM/Gas/POS Skimmer shim rules.  From Marc/Jay 2/13/15.  Added by gbassett
    try:
        if 'Skimmer' in incident['action']['physical']['variety']:
            logging.info('Adding attribute.confidentiality.data.variety=Payment, '
                         'attribute.integrity.variety = Hardware tampering and '
                         'action.misuse.variety.Unapproved hardware')
            # ensure attribute, integrity, and variety exist and set them to hardware tampering
            if 'attribute' not in incident:
                incident['attribute'] = {'integrity':{'variety':['Hardware tampering']}}
            elif 'integrity' not in incident['attribute']:
                incident['attribute']['integrity'] = {'variety': ['Hardware tampering']}
            else:
                if 'Hardware tampering' not in incident['attribute']['integrity']['variety']:
                    incident['attribute']['integrity']['variety'].append('Hardware tampering')
            # ensure cofidentiality, data, and variety are in the incident and add 'payment' to the list
            if 'confidentiality' not in incident['attribute']:
                incident['attribute']['confidentiality'] = {'data': [{'variety': 'Payment'}]}
            elif 'data' not in incident['attribute']['confidentiality']:
                incident['attribute']['confidentiality']['data'] = [{'variety': 'Payment'}]
            else:
                if 'Payment'.lower().strip() not in [x['variety'].lower().strip() for x in incident['attribute']['confidentiality']['data']]:
                    incident['attribute']['confidentiality']['data'].append({'variety': 'Payment'})
            # ensure action, misuse, and variety are in the incident and add 'Unapproved hardware' to the list
            if 'action' not in incident:
                incident['action'] = {'misuse':{'variety':['Unapproved hardware']}}
            elif 'misuse' not in incident['action']:
                incident['action']['misuse'] = {'variety':['Unapproved hardware']}
            else:
                if 'Unapproved hardware' not in incident['action']['misuse']['variety']:
                    incident['action']['misuse']['variety'].append('Unapproved hardware')
    except KeyError:
        logging.info('act.physical.variety not set so Skimmer (ATM/gas station/PoS skimmer shim) rule ignored.')


    # Handheld Skimmer rules.  From Marc/Jay 2/13/15.  Added by gbassett
    try:
        if 'Possession abuse' in incident['action']['misuse']['variety']:
            logging.info('Adding attribute.confidentiality.data.variety=Payment, '
                         'asset.assets.variety = M - Payment card, and '
                         'action.misuse.variety.Unapproved hardware')
            # ensure asset, assets, and variety are in the dictionary and set it to M - Payment card as it is a string
            if 'asset' not in incident:
                incident['asset'] = {'assets': [{'variety': 'M - Payment card'}]}
            elif 'assets' not in incident['asset']:
                incident['asset']['assets'] = [{'variety': 'M - Payment card'}]
            else:
                if 'M - Payment card'.lower().strip() not in [x['variety'].lower().strip() for x in incident['asset']['assets']]:
                    incident['asset']['assets'].append({'variety': 'M - Payment card'})
            # ensure confidentiality, data, and variety are in the incident and add 'payment' to the list
            if 'attribute' not in incident:
                incident['attribute'] = {'confidentiality': {'data': [{'variety': 'Payment'}]}}
            elif 'confidentiality' not in incident['attribute']:
                incident['attribute']['confidentiality'] = {'data': [{'variety': 'Payment'}]}
            elif 'data' not in incident['attribute']['confidentiality']:
                incident['attribute']['confidentiality']['data'] = [{'variety': 'Payment'}]
            else:
                if 'Payment'.lower().strip() not in [x['variety'].lower().strip() for x in incident['attribute']['confidentiality']['data']]:
                    incident['attribute']['confidentiality']['data'].append({'variety': 'Payment'})
            # ensure action, misuse, and variety are in the incident and add 'Unapproved hardware' to the list
            if 'action' not in incident:
                incident['action'] = {'misuse':{'variety':['Unapproved hardware']}}
            elif 'misuse' not in incident['action']:
                incident['action']['misuse'] = {'variety':['Unapproved hardware']}
            else:
                if 'Unapproved hardware' not in incident['action']['misuse']['variety']:
                    incident['action']['misuse']['variety'].append('Unapproved hardware')
    except KeyError:
        logging.info('act.misuse.variety not set so Possession abuse (handheld skimmer) rule ignored.')
    '''

    # Unknown victims have NAICS code of "000", not just one zero
    if incident['victim']['industry'].lower() in ['0','unknown']:
        incident['victim']['industry'] = "000"

    # KDT the script sometimes produces incidents with an asset array that has
    # no entries. I'm too lazy to figure out where that happens so I'll just
    # check for it here and fix it.
    if len(incident['asset']['assets']) < 1:
        incident['asset']['assets'].append({'variety':'Unknown'})

    return incident



## MAIN LOOP EXECUTION
def main():
    logging.info('Beginning main loop.')

    logging.info('Ending main loop.')

if __name__ == "__main__":

    ## Gabe
    ## The general Apprach to config parsing (Probably not the best way)
    ## 1. create a dictionary called 'cfg' of fallback values (up at the top of the file)
    ## 2. parse the arguments (args) and turn into a dictionary if the value is not None
    ## 3. Use the config from the command line parser to read the config file and update the 'cfg' dictionary
    ## 4. Update the cfg dictionary with the arguements (args) from the command line

    # 1. TODO


    # 2. TODO


    # 3. TODO


    # 4. TODO

    main()