""" Build Model for Spectrum """

# Packages
import numpy as np

# gelato supporting files
import gelato.CustomModels as CM
import gelato.AdditionalComponents as AC

# Build the model from continuum and emission
def BuildModel(continuum,emission):

    model = continuum+emission
    model.parameters[0:continuum.parameters.size] = continuum.parameters
    model.parameters[continuum.parameters.size:] = emission.parameters

    return model

# Build the emission lines from the EmissionGroups and spectrum with initial guess
def BuildEmission(spectrum, EmissionGroups=None):
    
    ## Build Base Model
    model_components = []
    param_names = []

    # Check if we were passed an emission lines
    if EmissionGroups == None:
        EmissionGroups = spectrum.p['EmissionGroups']

    # Over all emission lines
    for group in EmissionGroups:
        for species in group['Species']:
            for line in species['Lines']:
                name =  group['Name'] + '-' + species['Name'] + '-' + str(line['Wavelength']) + '-'
                
                # If additional component
                if species['Flag'] < 0:
                    model = AC.AddComponent(species['Flag'],line['Wavelength'],spectrum)
                    
                # IF original model component
                else:
                    model = CM.SpectralFeature(center = line['Wavelength'],spectrum = spectrum)

                # Add model
                model_components.append(model)
                
                # Collect param names
                for pname in model_components[-1].param_names:
                    param_names.append(name+pname)
    ## Build Base Model

    ## Tie parameters ##
    model = TieParams(spectrum,np.sum(model_components),param_names,EmissionGroups)
    ## Tie parameters ##

    return model,param_names

# Tie Model Parameters:
def TieParams(spectrum,model,param_names,EmissionGroups=None):

    if type(EmissionGroups) == type(None):
        EmissionGroups = spectrum.p['EmissionGroups']

    # Tie Continuum
    model = TieContinuum(model,param_names)

    # Tie Emission
    model = TieEmission(spectrum,model,param_names,EmissionGroups)

    return model

# Tie Continuum Redshift
def TieContinuum(cont,cont_pnames):

    first_redshift = True
    for pname in cont_pnames:
        if (('Redshift' in pname) and ('Continuum' in pname)):
            if first_redshift:
                TieRedshift = GenTieFunc(cont_pnames.index(pname))
                first_redshift = False
            else:
                cont.tied[cont.param_names[cont_pnames.index(pname)]] = TieRedshift

    return cont

# Tied Emission model parameters
def TieEmission(spectrum,model,param_names,EmissionGroups):

    ## Tie parameters ##
    for group in EmissionGroups:
        first_group_member = True

        for species in group['Species']:
            first_species_line = True
            first_species_flux = True

            for line in species['Lines']:
                
                # Find parameter name prefix
                name =  group['Name'] + '-' + species['Name'] + '-' + str(line['Wavelength']) + '-'

                ## Tie Group Components
                # Check for first line in group and make tie functions
                if first_group_member:
                    first_group_member = False
                    TieGroupRedshift = GenTieFunc(param_names.index(name+'Redshift'))
                    TieGroupDispersion = GenTieFunc(param_names.index(name+'Dispersion'))
                else:
                    # Otherwise tie redshift (check if we should)
                    if group['TieRedshift']:
                        model.tied[model.param_names[param_names.index(name+'Redshift')]] = TieGroupRedshift
                    # Otherwise tie dispersion (check if we should)
                    if group['TieDispersion']:
                        model.tied[model.param_names[param_names.index(name+'Dispersion')]] = TieGroupDispersion
                    
                ## Tie Species Components
                # Tie Dispersion and Redshift
                # Check for first line in species and make tie functions
                if first_species_line:
                    # Dispersion
                    first_species_line = False
                    TieSpeciesRedshift = GenTieFunc(param_names.index(name+'Redshift'))
                    TieSpeciesDispersion = GenTieFunc(param_names.index(name+'Dispersion'))

                # Otherwise tie params
                else:
                    # Dispersion and Redshift
                    model.tied[model.param_names[param_names.index(name+'Redshift')]] = TieSpeciesRedshift                
                    model.tied[model.param_names[param_names.index(name+'Dispersion')]] = TieSpeciesDispersion                

                # Tie Flux
                if (first_species_flux and (line['RelStrength'] != None)):
                    first_species_flux = False
                    # Flux
                    reference_flux = line['RelStrength']
                    index_flux = param_names.index(name+'Flux')
                elif (line['RelStrength'] != None):
                    height_index = param_names.index(name+'Flux')
                    TieFlux = GenTieFunc(index_flux,scale=line['RelStrength']/reference_flux)
                    model.tied[model.param_names[height_index]] = TieFlux
            
    ##Tie parameters ##

    return model

# Generate Tie Paramater Function, needed to preserve static values in function
# Note: tried using lambda function in place, but it didn't work. 
def GenTieFunc(index,scale=1):

    def TieFunc(model):
        return model.parameters[index]*scale

    return TieFunc