#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 23:55:01 2023

@author: yunusemreavci
"""

import utdf2gmns as ug
import pandas as pd
import re

class IntersectionCodeGenerator:

    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.intersections = {}
        self.df = pd.read_csv(self.csv_path)
        self.updated_df = None
        
    def gmnsmovement2code(self, direction_rows):
        right_lanes = left_lanes = thru_lanes = 0
        thru_shared = left_shared = right_shared = 0
        right_exists = left_exists = False 
        thru_exists = False
    
        # Extract lane counts and shared status
        for _, row in direction_rows.iterrows():
            movement = row['mvmt_txt_id'][-1]
            if movement == 'R':
                right_lanes = int(row['Lanes']) if pd.notna(row['Lanes']) else 0
                right_shared = int(row['Shared']) if pd.notna(row['Shared']) else 0
                right_exists = True
            elif movement == 'L':
                left_lanes = int(row['Lanes']) if pd.notna(row['Lanes']) else 0
                left_shared = int(row['Shared']) if pd.notna(row['Shared']) else 0
                left_exists = True
            elif movement == 'T':
                thru_lanes = int(row['Lanes']) if pd.notna(row['Lanes']) else 0
                thru_shared = int(row['Shared']) if pd.notna(row['Shared']) else 0
                thru_exists = True
        
        # Construct the code based on constraints
        code = ''
        
        if thru_exists and thru_lanes > right_shared + left_shared:
            code += 'T' + str(thru_lanes - right_shared - left_shared)
        if left_exists and left_lanes > left_shared:
            code += 'L' + str(left_lanes - left_shared) 
        if right_exists and right_lanes > right_shared:
            code += 'R' + str(right_lanes - right_shared) 
        if thru_exists and left_shared > 0:
            code += 'LS' + str(left_shared) 
        if thru_exists and right_shared > 0:
            code += 'RS' + str(right_shared)
        if not thru_exists and right_shared > 0  and left_shared > 0:
            code += 'LRS' + str(right_shared)
        # # Construct the code based on constraints
        # code = ''
        
        # if left_lanes > 0:
        #     code += 'L' + str(left_lanes)

        # if right_exists and right_lanes == 0 and shared == 2:
        #     if thru_lanes in {1, 2, 3}:
        #         if thru_lanes - 1 != 0:
        #             code = 'T' + str(thru_lanes-1) + code + 'RS1'
        #         else:
        #             code += 'RS1'
        # elif not thru_exists and right_lanes == 0 and left_lanes > 0 and left_shared == 2:
        #     if left_lanes == 1:
        #         code = 'L1R1'
        #     elif left_lanes == 2:
        #         code = 'L2R1'
        # elif not right_exists and thru_lanes == 3 and shared in {0, 2}:
        #     if code != '':
        #         code = 'T2' + code + 'RS1'
        #     else:
        #         code = 'T2RS1'
        # elif right_lanes == 1 and thru_lanes == 2 and shared == 0:
        #     if code != '':
        #         code = 'T1' + code + 'RS1'
        #     else:
        #         code = 'T1RS1'
        # elif right_lanes == 0 and left_lanes == 0 and thru_lanes > 0 and shared == 3:
        #     code = 'RLS' + str(thru_lanes)  # Overwrites previous code in case of RLS

        return code


    def process_intersections(self):
        for intersection_name in self.df['intersection_name'].unique():
            if pd.notna(intersection_name):
                intersection_rows = self.df[self.df['intersection_name'] == intersection_name]
                for direction in ['NB', 'SB', 'EB', 'WB']:
                    direction_rows = intersection_rows[intersection_rows['mvmt_txt_id'].str.startswith(direction)]
                    shared_code = self.gmnsmovement2code(direction_rows)
                    self.intersections[intersection_name] = self.intersections.get(intersection_name, {})
                    self.intersections[intersection_name][direction] = shared_code

    def get_intersection_codes(self):
        self.process_intersections()
        return self.intersections

    def read_updated_file(self, updated_csv_path):
        self.updated_df = pd.read_csv(updated_csv_path)

    def code2gmnsmovement(self, intersection_name, direction_code):
        parsed_data = []
        movements = direction_code.split(';')

        for movement in movements:
            direction = movement[:2]  # Extract direction (NB, SB, etc.)
            movement = movement[2:]   # Remaining movement code

            # Initialize default lane count and shared status
            lane_counts = {'T': 0, 'L': 0, 'R': 0, 'U': 0}
            shared_status = {'T': 0, 'L': 0, 'R': 0, 'U': 0}

            # Extract movement types and lane counts
            movement_matches = re.findall(r'([TRLU])(\d+)', movement)
            for match in movement_matches:
                movement_type, num_lanes = match
                lane_counts[movement_type] = int(num_lanes)

            # Apply reverse logic for shared lanes
            if 'RLS' in movement:
                shared_lanes = int(re.search(r'RLS(\d+)', movement).group(1))
                shared_status['T'] = shared_status['L'] = shared_status['R'] = 3
                lane_counts['T'] = shared_lanes
                lane_counts['L'] = lane_counts['R'] = 0
            elif 'RS' in movement:
                shared_lanes = int(re.search(r'RS(\d+)', movement).group(1))
                shared_status['T'] = 3 if lane_counts['T'] > 0 else 0
                shared_status['R'] = 0
                lane_counts['R'] = shared_lanes if 'R' not in movement else lane_counts['R']
            elif 'LS' in movement:
                shared_lanes = int(re.search(r'LS(\d+)', movement).group(1))
                shared_status['T'] = 2 if lane_counts['T'] > 0 else 0
                shared_status['L'] = 0
                lane_counts['L'] = shared_lanes if 'L' not in movement else lane_counts['L']

            # Create data entries
            for movement_type, lanes in lane_counts.items():
                if lanes > 0 or (lanes == 0 and shared_status[movement_type] > 0):
                    data = {
                        "Intersection Name": intersection_name,
                        "Direction": direction,
                        "Movement Type": movement_type,
                        "Number of Lanes": lanes,
                        "Shared Movement Type": shared_status[movement_type]
                    }
                    parsed_data.append(data)

        return parsed_data

    def parse_all_intersections(self):
        all_parsed_data = []
        for _, row in self.updated_df.iterrows():
            intersection_name = row['intersection_name']
            combined_code = row['intersection_code']
            if pd.notna(combined_code) and isinstance(combined_code, str):
                parsed_data = self.code2gmnsmovement(intersection_name, combined_code)
                all_parsed_data.extend(parsed_data)
        return pd.DataFrame(all_parsed_data)

    def transform_parsed_data(self, parsed_df):
        # Define all possible movement types
        movement_types = ['NBL', 'NBT', 'NBR', 'SBL', 'SBT', 'SBR', 'EBL', 'EBT', 'EBR', 'WBL', 'WBT', 'WBR']

        # Create a multi-index for columns (Movement Type, Data Type)
        multi_index = pd.MultiIndex.from_product([movement_types, ['Lanes', 'Shared']],
                                                 names=['Movement Type', 'Data Type'])

        # Initialize the transformed DataFrame
        transformed_df = pd.DataFrame(columns=multi_index)
        rows = []

        for intersection_name in parsed_df['Intersection Name'].unique():
            intersection_data = parsed_df[parsed_df['Intersection Name'] == intersection_name]
            intersection_dict = {}

            for movement in movement_types:
                match = intersection_data[(intersection_data['Direction'] + intersection_data['Movement Type']) == movement]
                if not match.empty:
                    lanes = match.iloc[0]['Number of Lanes']
                    shared = match.iloc[0]['Shared Movement Type']
                    intersection_dict[(movement, 'Lanes')] = lanes
                    intersection_dict[(movement, 'Shared')] = shared

            # Append the data for this intersection to the rows list
            rows.append(pd.Series(intersection_dict, name=intersection_name))

        # Concatenate all rows to form the DataFrame
        transformed_df = pd.concat(rows, axis=1).T
        return transformed_df

    def process_and_transform_intersections(self, updated_csv_path):
        self.read_updated_file(updated_csv_path)
        parsed_df = self.parse_all_intersections()
        return self.transform_parsed_data(parsed_df)

    
    def create_intersection_code_table(self,intersections):
        # Prepare the data for the DataFrame
        data = []
        for intersection_name, directions in intersections.items():
            combined_code = ';'.join([f"{dir_code}{code}" for dir_code, code in directions.items() if code])
            data.append([intersection_name, combined_code])
    
        # Create the DataFrame
        df = pd.DataFrame(data, columns=['intersection_name', 'intersection_code'])
    
        return df
    
    def append_and_save_combined_codes(self):
        # Initialize a new column for combined codes with empty strings
        self.df['intersection_code'] = ''

        # Iterate over the intersections to update the DataFrame
        for intersection_name, directions in self.intersections.items():
            combined_code = ';'.join([f"{dir_code}{code}" for dir_code, code in directions.items() if code])

            # Find the index of the first occurrence of the intersection_name
            first_index = self.df[self.df['intersection_name'] == intersection_name].index[0]

            # Assign the combined code only to the first occurrence
            self.df.at[first_index, 'intersection_code'] = combined_code

        # Save the updated DataFrame back to a new CSV file
        updated_csv_path = self.csv_path
        self.df.to_csv(updated_csv_path, index=False)
        print(f"Updated CSV saved to {updated_csv_path}")
