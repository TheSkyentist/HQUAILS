#! /usr/bin/env python

""" Wrapper for single HQUAILS run """

# Packages
import sys
import argparse

# HQUAILS supporting files
import HQUAILS
import ConstructParams as CP

# Main Function
if __name__ == "__main__":

    HQUAILS.header()

    ## Parse Arguements to find Parameter File ##
    parser = argparse.ArgumentParser()
    parser.add_argument('Parameters', type=str, help='Path to parameters file')
    parser.add_argument('Spectrum', type=str, help='Path to spectrum.')
    parser.add_argument('Redshift', type=float, help='Redshift of object')
    args = parser.parse_args()
    p = CP.construct(args.Parameters)
    ## Parse Arguements to find Parameter File ##

    ## Run HQUAILS ##
    HQUAILS.HQUAILS(p, args.Spectrum, args.Redshift)

    HQUAILS.footer()