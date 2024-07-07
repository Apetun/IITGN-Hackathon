from query_handler import handle_query


def process_question_file(input_file, output_file):
    res = []
    with open(input_file, 'r') as infile:
        lines = infile.readlines()
        for line in lines:
            res.append(line.strip("\n"))
        
    out = []
    for i in range(0,len(res)):
        print(str(i+1)+")"+res[i])
        result = handle_query(res[i])
        print("Answer:"+result[1])
        out.append(result[1])
    
    with open(output_file, 'w') as outfile:
        for ans in out:
            outfile.write(ans + '\n')

input_file = './questions.txt'
output_file = './answers.txt'

process_question_file(input_file, output_file)