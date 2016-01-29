from WebAPI.Variant.MAFVariant import MAFVariant
from WebAPI.Variant.vepConsequenceVariant import vepConsequenceVariant
#{
#	"allele_string": "G/A",
#	"assembly_name": "GRCh37",
#	"colocated_variants": [
#		{
#			"allele_string": "G/A",
#			"end": 140534527,
#			"id": "COSM1312758",
#			"phenotype_or_disease": 1,
#			"seq_region_name": "7",
#			"somatic": 1,
#			"start": 140534527,
#			"strand": 1
#		}
#	],
#	"end": 140534527,
#	"id": null,
#	"input": "7 140534527 . G A . . .",
#	"most_severe_consequence": "missense_variant",
#	"seq_region_name": "7",
#	"start": 140534527,
#	"strand": 1,
#	"transcript_consequences": [
#		{
#			"biotype": "retained_intron",
#			"cdna_end": 392,
#			"cdna_start": 392,
#			"consequence_terms": [
#				"non_coding_transcript_exon_variant",
#				"non_coding_transcript_variant"
#			],
#			"exon": "3/3",
#			"gene_id": "ENSG00000157764",
#			"gene_symbol": "BRAF",
#			"gene_symbol_source": "HGNC",
#			"hgnc_id": 1097,
#			"hgvsc": "ENST00000469930.1:n.392C>T",
#			"impact": "MODIFIER",
#			"strand": -1,
#			"transcript_id": "ENST00000469930",
#			"variant_allele": "A"
#		},
#		{
#			"amino_acids": "S/L",
#			"biotype": "protein_coding",
#			"canonical": 1,
#			"ccds": "CCDS5863.1",
#			"cdna_end": 447,
#			"cdna_start": 447,
#			"cds_end": 386,
#			"cds_start": 386,
#			"codons": "tCa/tTa",
#			"consequence_terms": [
#				"missense_variant"
#			],
#			"domains": [
#				{
#					"db": "hmmpanther",
#					"name": "PTHR23257"
#				},
#				{
#					"db": "hmmpanther",
#					"name": "PTHR23257"
#				}
#			],
#			"exon": "3/18",
#			"gene_id": "ENSG00000157764",
#			"gene_symbol": "BRAF",
#			"gene_symbol_source": "HGNC",
#			"hgnc_id": 1097,
#			"hgvsc": "ENST00000288602.6:c.386C>T",
#			"hgvsp": "ENSP00000288602.6:p.Ser129Leu",
#			"impact": "MODERATE",
#			"polyphen_prediction": "benign",
#			"polyphen_score": 0.003,
#			"protein_end": 129,
#			"protein_id": "ENSP00000288602",
#			"protein_start": 129,
#			"refseq_transcript_ids": [
#				"NM_004333.4"
#			],
#			"sift_prediction": "tolerated",
#			"sift_score": 0.2,
#			"strand": -1,
#			"transcript_id": "ENST00000288602",
#			"variant_allele": "A"
#		},
#		{
#			...
#       }
#       ]
#   },

class vepVariant(MAFVariant):
	def __init__(self , **kwargs):
		super(vepVariant,self).__init__(**kwargs)
		self.inputVariant = kwargs.get('inputVariant',"")
		self.consequences = kwargs.get('consequences',[])
		self.annotations = kwargs.get('annotations',{})
		aParentVariant = kwargs.get( 'parentVariant' , None )
		if aParentVariant:
			super( vepVariant , self ).copyInfo( aParentVariant )
	def copyInfo( self , copy ):
		super( vepVariant , self ).copyInfo( copy )
		self.inputVariant = copy.inputVariant
		self.consequences = copy.consequences
		self.annotations = copy.annotations

	def printVariant(self,delim , **kwargs ):
		onlyThisVariant = kwargs.get( 'minimal' , False )
		if not onlyThisVariant:
			super(vepVariant,self).printVariant( delim , **kwargs )
		print "vepVariant: " ,
		if self.inputVariant:
			print "inputVariant=" ,
			print self.inputVariant + delim ,
		if self.consequences:
			print "consequences= ["
			for cons in sorted(self.consequences):
				cons.printVariant(delim,**kwargs)
			print "]" + delim ,
		if self.annotations:
			print "annotations => {" ,
			for anno in sorted(self.annotations.keys()):
				print str(anno) + " => " + str(self.annotations.get( cons ) ) + delim ,
			print "}" + delim ,
		print ""
	def attr(self):
		attributes = super(vepVariant,self).attr()
		if self.inputVariant:
			attributes.append(self.inputVariant)
		if self.consequences:
			attributes.append(self.consequences)
		if self.annotations:
			attributes.append(self.annotations)
		return attributes

	def printConsequencesProteogenomicVar( self ):
		print self.proteogenomicVar()
		for consequence in self.consequences:
			print self.genomicVar() + ", " ,
			print consequence.codingHGVS()

	def parseEntryFromVEP( self , rootElement ):
		''' Expect rootElement as JSON (dict) '''
		print "WebAPI::Variant::vepVariant::parseEntryFromVEP"
		print rootElement
		self.chromosome = rootElement.get( 'seq_region_name' )
		self.start = rootElement.get( 'start' )
		self.stop = rootElement.get( 'end' )
		allele_string = rootElement.get( 'allele_string' ).split('/')
		self.reference = allele_string[0]
		if len( allele_string ) > 1:
			self.alternate = allele_string[1]
		else:
			self.alternate = allele_string[0]
		self.strand = rootElement.get( 'strand' )
		self.assembly = rootElement.get( 'assembly_name' )
		print "variant info set"
		self.printVariant(', ')
		mostSevereConsequence = rootElement.get( 'most_severe_consequence' )
		transcriptConsequences = rootElement.get( 'transcript_consequences' )
		self.setTranscriptConsequences( transcriptConsequences )
		print "\nall parsed and set"
		self.printVariant(', ')
		print "\n\n"
	def setTranscriptConsequences( self , transcriptConsequences ):
		''' Expect transcriptConsequences as dict from JSON '''
		print "WebAPI::Variant::vepVariant::setTranscriptConsequence"
		self.printVariant(', ')
		i = 0
		for consequence in transcriptConsequences: #list of dict's
			print "consequence " + str(i)
			i += 1
			otherVar = vepConsequenceVariant( parentVariant=self )
			otherVar.printVariant('__')
			otherVar.parseTranscriptConsequence( consequence )
			self.consequences.append( otherVar )
		print "consequences set"
		self.printVariant(', ')
