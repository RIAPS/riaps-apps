#!/bin/sh

riaps_lang TransactiveEnergy.riaps
riaps_depll -g TransactiveEnergy.depl
cp TransactiveEnergy.json ../pkg/
cp TransactiveEnergy-deplo.json ../pkg/
cp ../.env ../pkg/libs/
