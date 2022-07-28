import sys

def main():

    # initial filenames
    script_name = ''
    input_one = ''
    input_two = ''
    name = ''

    # get args
    if len(sys.argv) == 3:
        print('number of arguments: ', len(sys.argv))
        script_name = sys.argv[0]
        input_one = sys.argv[1]
        input_two = sys.argv[2]
    else:
        print('ERROR: WRONG ARGUMENTS')
        sys.exit(0)

    compare(input_one, input_two)

def compare(input_one, input_two):

    print('-- compare called --')

    input_one_count = 0
    input_two_count = 0

    with open(input_one) as f:
        for line in f:
            #print (line)

            if '<trkpt' in line:
                input_one_count += 1
        
    with open(input_two) as f:
        for line in f:
            #print (line)

            if '<trkpt' in line:
                input_two_count += 1

    print('input_one_count: ', input_one_count)
    print('input_two_count: ', input_two_count)

if __name__ == "__main__":
    main()