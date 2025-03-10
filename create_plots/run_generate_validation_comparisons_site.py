# run_generate_validation_comparisons_site.py
# June 2022

# This is the main run script that sets parameters and calls the core function to create validation comparisons for
# each validation relationship. All site-specific simulation results are plotted and compared against their associated
# reference dataset.

from manifest import simulation_output_filepath, benchmark_simulation_filepath, \
     base_reference_filepath, plot_output_filepath, comps_id_folder
from simulations.helpers import load_coordinator_df
from simulations.get_version import get_era_version_from_file
from helpers_coordinate_each_relationship import generate_age_incidence_outputs, \
    generate_age_prevalence_outputs, generate_parasite_density_outputs, generate_infectiousness_outputs, \
    generate_age_infection_duration_outputs
from datetime import datetime
import shutil
import argparse
import os

era_version = get_era_version_from_file()
simulation_output_filepath = simulation_output_filepath
if not os.path.exists(benchmark_simulation_filepath):
    benchmark_simulation_filepath = simulation_output_filepath


def run(subset="All"):
    # read in data and create plots
    coord_csv = load_coordinator_df(set_index=False)
    print(f"plotting with subset = {subset}.")
    if plot_output_filepath.is_dir():
        date, time = datetime.now().strftime("%d-%m-%Y %H-%M-%S").split(' ')
        plot_output_bak_filepath = plot_output_filepath.parent / (str(plot_output_filepath.name) + f'_{date}_{time}_backup')
        print(f"Folder {plot_output_filepath} is already there."
              f"Copying existing files to folder {plot_output_bak_filepath}.")
        shutil.move(plot_output_filepath, plot_output_bak_filepath)
    try:
        plot_output_filepath.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"Folder {plot_output_filepath} is already there. "
              f"Suggest to save a backup or the existing files and create an empty folder for new file.")
    else:
        print(f"Folder {plot_output_filepath} was created")

    if subset.lower() == "all" or "core_relationship" in subset.lower():

        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
        #                         age - incidence                         #
        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
        generate_age_incidence_outputs(coord_csv, simulation_output_filepath, base_reference_filepath, plot_output_filepath,
                                       benchmark_simulation_filepath=benchmark_simulation_filepath)

        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
        #                         age - prevalence                        #
        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
        generate_age_prevalence_outputs(coord_csv, simulation_output_filepath, base_reference_filepath, plot_output_filepath,
                                        benchmark_simulation_filepath=benchmark_simulation_filepath)

        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
        #                      age - parasite density                     #
        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
        generate_parasite_density_outputs(coord_csv, simulation_output_filepath, base_reference_filepath, plot_output_filepath,
                                           benchmark_simulation_filepath=benchmark_simulation_filepath)

        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
        #                   infectiousness to vectors                        #
        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
        generate_infectiousness_outputs(coord_csv, simulation_output_filepath, base_reference_filepath, plot_output_filepath,
                                        benchmark_simulation_filepath=benchmark_simulation_filepath)

    if subset.lower() == "all" or "infection_duration" in subset.lower():
        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
        #                    age - infection duration                     #
        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
        # set positive threshold density for sampled parasites in simulation output (to match PCR threshold in reference)
        pos_thresh_dens = 0.5  # Note: from the reference dataset, the smallest positive density was 39. (39=min(ref_df$DENSITY[ref_df$DENSITY>0], na.rm=TRUE) - 1)
        # specify binning for duration of infection
        duration_bins = list(range(0, 400, 50))
        duration_bins.append(500)
        generate_age_infection_duration_outputs(coord_csv, simulation_output_filepath, base_reference_filepath,
                                                plot_output_filepath, pos_thresh_dens, duration_bins,
                                                benchmark_simulation_filepath=benchmark_simulation_filepath)
    # generate dummy file for snakemake plot rule.
    if not os.path.isdir(comps_id_folder):
        os.mkdir(comps_id_folder)
    with open(comps_id_folder / 'report_completed', 'w') as file:
        file.write('Plotting is completed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process site name')
    parser.add_argument('--subset', '-s', type=str, help='subset name(s)',
                        default="All")

    args = parser.parse_args()
    run(subset=args.subset)
