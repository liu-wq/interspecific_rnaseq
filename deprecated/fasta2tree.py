#!/usr/bin/env python
''' 
This script takes a directory of fasta files, aligns them using translatorX, and estimates a tree using raxml, partitioned by codon
Need to adjust translatorx script path and raxml command
Needs mafft in the PATH
'''
import glob, os
import sys
from Bio import AlignIO

translatorx_path = '/home/dbstern/Programs/translatorx_vLocal.pl'
raxml_cmd = 'raxmlHPC-PTHREADS-AVX -T 16'

def transx(fasta_file,DIR):
	transout = fasta_file.split('.')[0]+".transx"
	command = "perl "+translatorx_path+" -i "+DIR+fasta_file+" -o "+DIR+transout+" -p F -c 1 -t T"
	print "executing: " + command
	os.system(command)
	
def partition(alignment,DIR):
	ali = AlignIO.read(DIR+alignment, "fasta")
	length = str(ali.get_alignment_length())
	output = open(DIR+"partition.PART", "w")
	output.write("DNA, p1 = 1-"+length+"\\3\nDNA, p2 = 2-"+length+"\\3\nDNA, p3 = 3-"+length+"\\3\n")

def seqcount(alignment):
	count = 0
	for fasta in alignment:
		count += 1
	return count
	
def tree(alignment,DIR):
	ali = AlignIO.read(DIR+alignment, "fasta")
	if seqcount(ali) < 500:
		cluster = alignment.split('.')[0]
		command = raxml_cmd+" -f d -m GTRCAT -p 1293049 -# 10 -q "+DIR+"partition.PART -s "+DIR+alignment+" -w "+os.path.abspath(DIR)+" -n "+cluster
		print "executing: " + command
		os.system(command)
		tree = DIR+cluster+".raxml.tre"
		raw_tree = DIR+"RAxML_bestTree."+cluster
		try:
			os.rename(raw_tree,tree)
			os.remove(DIR+"RAxML_*")
			os.remove(DIR+cluster+".reduced*")
		except:pass 
	else:
		cluster = alignment.split('.')[0]
		command = 'FastTree -gtr -nt '+DIR+alignment+' > '+DIR+cluster+'.fasttree.tre'
		os.system(command)

if __name__ == "__main__":
	DIR, ending = sys.argv[1:]
	if DIR[-1] != "/": DIR += "/"
	for fasta_file in os.listdir(DIR):
		if fasta_file.endswith(ending):
			cluster = fasta_file.split('.')[0]
			if os.path.isfile(DIR+cluster+'.transx.nt_ali.fasta'):
				print('Detected alignment for '+cluster)
			else:
				transx(fasta_file,DIR)
				os.system('rm '+DIR+'*.html '+DIR+'*nt1_ali.fasta '+DIR+'*nt2_ali.fasta '+DIR+'*nt3_ali.fasta '+DIR+'*nt12_ali.fasta '+DIR+'*.log '+DIR+'*.aaseqs '+DIR+'*.aaseqs.fasta '+DIR+'*aa_based_codon* '+DIR+'*.aa_ali.fasta')
	for fasta_file in os.listdir(DIR):
		if fasta_file.endswith(ending):
			cluster = fasta_file.split('.')[0]
			if os.path.isfile(DIR+cluster+'.raxml.tre') or os.path.isfile(DIR+cluster+'.fasttree.tre'): 
				print('Detected tree file for '+cluster)
			else:
				partition(cluster+".transx.nt_ali.fasta",DIR)
				tree(cluster+".transx.nt_ali.fasta",DIR)