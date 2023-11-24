#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 14:05:44 2023

@author: yunusemreavci
"""

import os
import osm2gmns as og
import utdf2gmns as ug



class UTDFGenerator:
    def __init__(self, map_folder):
        self.map_folder = map_folder
        
    def getInitialNet(self):
        # choose link_types from 'motorway', 'trunk','primary','secondary', 'tertiary', 'residential'. default: 'all'
        net = og.getNetFromFile(filename=os.path.join(self.map_folder, 'bullhead_city.osm'),
                                network_types=('auto'),
                                default_lanes=True)
        og.consolidateComplexIntersections(net, auto_identify=True, int_buffer=20.0)
        
        og.generateNodeActivityInfo(net)
        og.buildMultiResolutionNets(net)
        og.outputNetToCSV(net, output_folder=self.map_folder)
    
    def regenerateNet_based_on_macroNet(self):
        net = og.loadNetFromCSV(folder=self.map_folder,
                                node_file='node.csv', link_file='link.csv', 
                                movement_file='movement_utdf.csv')
        # The consolidation function is needed if we changed 'main_node_id' of some nodes in node.csv in Stage 2.
        og.consolidateComplexIntersections(net, auto_identify=True)
    
        og.buildMultiResolutionNets(net)
    
        og.outputNetToCSV(net, output_folder=self.map_folder)
 
map_folder = r"/Users/yunusemreavci/Desktop/intersection-code/bullhead/"
generator = UTDFGenerator(map_folder)
generator.getInitialNet()
res = ug.generate_movement_utdf(map_folder, "Bullhead City",isSave2csv=True)
# generator.regenerateNet_based_on_macroNet()