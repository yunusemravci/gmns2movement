#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 01:15:59 2023

@author: yunusemreavci
"""

import utdf2gmns as ug
import IntersectionCodeGenerator
import osm_intersection

# map_folder = r"/Users/yunusemreavci/Desktop/intersection-code/bullhead/"
# generator = UTDFGenerator(map_folder)
# generator.getInitialNet()
# res = ug.generate_movement_utdf(map_folder, "Bullhead City",isSave2csv=True)

# Usage
csv_path = r"/Users/yunusemreavci/Desktop/intersection-code/bullhead/movement_utdf.csv"
# csv_path = r"/Users/yunusemreavci/Desktop/intersection-code/bullhead/movement_utdf.csv"
generator = IntersectionCodeGenerator(csv_path)
generator.process_intersections()
intersections = generator.get_intersection_codes()
print(intersections)
generator.append_and_save_combined_codes()  # Append and save the combined codes

# show out the intersections as a table 
intersection_code_table = generator.create_intersection_code_table(intersections)
print(intersection_code_table)

# Save to CSV
intersection_code_table.to_csv('intersection_codes_bullhead.csv', index=False)

# Intersection code to gmns movement
transformed_df = generator.process_and_transform_intersections(csv_path)
print(transformed_df)
transformed_df.to_csv("/Users/yunusemreavci/Desktop/intersection-code/bullhead/parsed_intersection_bullhead.csv")