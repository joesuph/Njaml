##############################
# TODO: Add Error conditions 
##############################


from cProfile import run
import re
from textwrap import indent
class Njaml():
    def __init__(self, indent_spaces=2):
        self.functions = dict()
        self.links = dict()
        self.asserts = dict()
        self.cases = dict()
        self.indent_spaces=indent_spaces

    def extract_name(self,text):
        """Extract function_name from njaml_line string"""
        return re.search("[a-zA-Z]+[0-9]*(_[a-zA-Z]+[0-9]*)*",text).group()


    def get_indices_of_indent_amount(self,lines,indent):
        """From a list of njaml_lines, get indices of lines with <indent param> indents"""
        #from list of lines, get the indices of indent level 
        return [ i for i in range(len(lines)) if re.search("^" + "\\s"*((indent)*self.indent_spaces) +"[a-zA-Z]",lines[i]) ] 

    def get_names_of_indent_amount(self,lines,indent):
        """From a list of njaml_lines, return the names of the functions with indent amount <indent param> """
        #from list of lines, get the names of indent level 
        return [ self.extract_name(line) for line in lines if re.search("^" + "\\s"*((indent)*self.indent_spaces) +"[a-zA-Z]",line) ] 

    def load_functions(self,lines,indent_amount):
        """
            From a list of njaml lines, and an indent_amount,
            add the functions of lines of indices to self.functions dict pointing to an array of it's
            childrens names

                input:
                    ["outer1","  lvl2_1","    lvl3_1","  lvl2_2","outer2"]
                result effect:
                    self.functions = {"outer1":["lvl2_1","lvl2_2"],"outer2":[],"lvl2_1":["lvl3_1"],"lvl2_2":[]}
        """
        #Get indices where lines start w/ an <indent_amount> number of indents
        indices = self.get_indices_of_indent_amount(lines,indent_amount)

        #Between each index is a parent function and just its children functions, 
        #For each region, get children functions and in self.functions dict point parent function to array of children.
        for i in range(len(indices)-1):

            #Get sublist just including the line with indent amount indent_amount and the lines nested under it
            subsection = lines[indices[i]:indices[i+1]]

            #set self.functions[function_name] = [list of nested children function names]
            self.functions[self.extract_name(lines[indices[i]])] = self.get_names_of_indent_amount(subsection,indent_amount+1)


        last_subsection = lines[indices[len(indices)-1]:]
        self.functions[self.extract_name(lines[indices[len(indices)-1]])] = self.get_names_of_indent_amount(last_subsection,indent_amount+1)
        
        #If there is an indent level after this one, run this function again on the next level to add those functions
        next_indent_indices = self.get_indices_of_indent_amount(lines,indent_amount+1)        
        if len(next_indent_indices) != 0:
            self.load_functions(lines,indent_amount+1)

 
    def load(self,file_name):
        """From an njaml file load the names of the functions and how they are nested into self.functions"""

        #Get Text
        txt = open(file_name, "r").read()

        #Remove blank and comment lines and put in array
        code_lines = list(filter(lambda x: not re.search(r"^\s*#",x) and re.search(r"[a-zA-Z]+",x),txt.split("\n")))
        
        #Load the functions Recursively
        self.load_functions(code_lines,0)

    def link(self,function_name,function):
        """Associates a njaml function with a python function defintion. """
        if not function_name in self.functions:
            raise Exception(f"function_name '{function_name}' was not loaded")
        self.links[function_name] = function
    
    def set_cases(self,function_name,inputs,outputs):
        """Set unit test inputs and outputs for a function"""
        if not function_name in self.functions:
            raise Exception(f"function_name '{function_name}' was not loaded")
        self.cases[function_name] = [inputs,outputs]

    def add_case(self,function_name,input,output):
        """Adds a single input and output pair to a functions unit test list"""
        if not function_name in self.functions:
            raise Exception(f"function_name '{function_name}' was not loaded")
        if function_name in self.cases:
            self.cases[function_name][0].append(input)
            self.cases[function_name][1].append(output)
        else:
            self.cases[function_name] = [[input],[output]]

    def run_cases(self,function_name,inputs=None,output_file=None):
        """Calls self.run(function_name,...) on each input and compare it to the output, then prints
            to console which ones matched and which ones didn't """
        if not function_name in self.cases:
             raise Exception(f"function_name '{function_name}' does not have case tests")
        passed = 0
        failed = 0
        
        #For each input and output case compare the two, if they match print pass, else print fail
        for i in range(len(self.cases[function_name][0])):
            input = self.cases[function_name][0][i]
            output = self.cases[function_name][1][i]
            try:
                result = self.run(function_name,input)
                if result != output:
                    raise Exception(f"{function_name}({input}) = {result} and != {output}")
            except Exception as e:
                print(f"Case {i} failed: {e}")
                failed += 1
            else:
                print(f"Case {i} passed")
                passed += 1
        print(f"{passed} passed.\n{failed} failed.")
            
           
    def run(self,function_name,args,output_file=None,file=None):
        """Run function_name with args and pipe the output from nested function to nested function
            until all nested functions have processed and return output.
        """
        #If output file supplied, open file for nested children to write outputs to
        if output_file != None:
            file = open(output_file,'w')
        
        output = args

        #If function has a python function associated with it, run input through python and continue with output
        if function_name in self.links:
            output = self.links[function_name](output)

        #If a file is open write the output to the file
        if file!=None:
            file.write(f"{function_name}: {str(output)}" + "\n\n")

        #Pipe the output through children functions
        for func in self.functions[function_name]:
            output = self.run(func,output,None,file)
        
        #Close output file we wrote to
        if output_file != None:
            file.close()
        return output


"""
Example:
    njaml = Njaml()

    #Load njaml functions
    njaml.load("file.njaml")

    print(njaml.functions)

    njaml.link('inner11',lambda x: x + 2)
    njaml.link('inner111',lambda x: x * 2)
    njaml.link('inner12',lambda x: x + 2)

    njaml.set_cases('outer1',[2,3],[10,12])

    print(njaml.run_cases("outer1"))

Njaml file:

outer1
  inner11
    inner111
  inner12

outer2
  inner21
"""
