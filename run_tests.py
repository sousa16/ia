import os
import glob
import subprocess
import difflib

# Clear the test_results.txt file
open('test_results.txt', 'w').close()


def run_test(input_file, expected_output_file):
    # Run your program with the input file as input
    result = subprocess.run(['/usr/bin/python3', 'pipe.py'],
                            stdin=open(input_file, 'r'), stdout=subprocess.PIPE)

    # Read the expected output
    with open(expected_output_file, 'r') as file:
        expected_output = file.read()

    # Compare the output to the expected output
    diff = difflib.unified_diff(expected_output, result.stdout.decode())

    # If there's a difference, print it
    diff_output = '\n'.join(list(diff))
    if diff_output:
        print(f'Difference found for {input_file}:')
        print('Expected output:')
        print(expected_output)
        print('Actual output:')
        print(result.stdout.decode())
        with open('test_results.txt', 'a') as file:
            file.write(f'Difference found for {input_file}:\n')
            file.write('Expected output:\n')
            file.write(expected_output + '\n')
            file.write('Actual output:\n')
            file.write(result.stdout.decode() + '\n')


# Get a list of all input files in the directory
input_files = glob.glob('test_1-9/test*.txt')

for input_file in input_files:
    # Construct the name of the corresponding output file
    expected_output_file = input_file.replace('.txt', '.out')

    # Run the test
    run_test(input_file, expected_output_file)
