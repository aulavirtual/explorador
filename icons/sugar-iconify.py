#!/usr/bin/python

import sys
import xml.dom.minidom
import getopt
import re
import os
import string

#define help output
def usage():
    print '\nUsage: sugar-iconify.py [options] input.svg\n'
    print 'Options:\n'
    print '\t -c\t\tApply default color entities (#666666, #ffffff) to output'
    print '\t -d directory\tThe preferred output directory'
    print '\t -e\t\tDo not insert entities for strokes and fills'
    print '\t -f hex\t\tHex value to replace with fill entity'
    print '\t -g\t\tAutomatically accept guesses for stroke and fill entities'
    print '\t -h\t\tDisplay this help message'
    print '\t -i\t\tInsert "isolated stroke" entities'
    print '\t -m\t\tMultiple export; export top level groups as separate icons' 
    print '\t -o\t\tOverwrite the input file; overridden by -m'
    print '\t -p pattern\tOnly export icons whose name matches pattern; for use with -m'
    print '\t -s hex\t\tHex value to replace with stroke entity'
    print '\t -x\t\tOutput example SVGs, for previewing their appearance in Sugar; ignored with -m'
    print '\t -v\t\tverbose'

#check for valid arguments
try:
    opts,arg = getopt.getopt(sys.argv[1:], "s:f:gcd:imp:oehvx")
except:
    usage()
    sys.exit(2)
        
if len(arg) < 1:
    usage()
    sys.exit(2)

#declare variables and constants
default_stroke_color = '#666666'
default_fill_color = '#ffffff'
transparent_color = '#00000000'
stroke_color = default_stroke_color
fill_color = default_fill_color
stroke_entity = "stroke_color"
fill_entity = "fill_color"
iso_stroke_entity = "iso_stroke_color"

output_path = ''
pattern = ''
entities_passed = 0
use_default_colors = False
confirm_guess = True
use_entities = True
multiple = False
verbose = False
overwrite_input = False
output_examples = False
use_iso_strokes = False

#interpret arguments
for o, a in opts:
    
    if o == '-s':
        stroke_color = '#' + a.lstrip('#').lower()
        entities_passed += 1
    elif o == '-f':
        fill_color = '#' + a.lstrip('#').lower()
        entities_passed += 1
    elif o == '-g':
        confirm_guess = False
    elif o == '-c':
        use_default_colors = True
    elif o == '-o':
        overwrite_input = True
    elif o == '-d':
        output_path = a.rstrip('/') + '/'
    elif o == '-e':
        use_entities = False
    elif o == '-v':
        verbose = True
    elif o == '-p':
        pattern = a
    elif o == '-h':
        usage()
        sys.exit(2)
    elif o == '-m':
        multiple = True
    elif o == '-x':
        output_examples = True
    elif o == '-i':
        use_iso_strokes = True

#isolate important parts of the input path
svgfilepath = arg[0].rstrip('/')
svgdirpath, sep, svgfilename = svgfilepath.rpartition('/')
svgbasename = re.sub(r'(.*)\.([^.]+)', r'\1', svgfilename)

#load the SVG as text
try:
    svgfile = open(svgfilepath, 'r')
except:
    sys.exit('Error: Could not locate ' + svgfilepath)

try:
    svgtext = svgfile.read()
    svgfile.close()
except:
    svgfile.close()
    sys.exit('Error: Could not read ' + svgfilepath)

#determine the creator of the SVG (we only care about Inkscape and Illustrator)
creator = 'unknown'

if re.search('illustrator', svgtext, re.I):
    creator = 'illustrator'
elif re.search('inkscape', svgtext, re.I):
    creator = 'inkscape'

if verbose:
    print 'The creator of this svg is ' + creator + '.'

#hack the entities into the readonly DTD
if use_entities:
    
    #before replacing them, we read the stroke/fill values out, should they have previously been defined,
    #to prevent needing to make guesses for them later
    stroke_match = re.search(r'stroke_color\s*\"([^"]*)\"', svgtext)
    fill_match = re.search(r'fill_color\s*\"([^"]*)\"', svgtext)
    if stroke_match is not None:
        stroke_color = stroke_match.group(1).lower()
        entities_passed += 1
    if fill_match is not None:
        fill_color = fill_match.group(1).lower()
        entities_passed += 1

    #define the entities
    if fill_match and stroke_match:
        entities  = '\t<!ENTITY ' + stroke_entity + ' "' + stroke_color + '">\n'
        entities += '\t<!ENTITY ' + fill_entity   + ' "' + fill_color   + '">\n'
        if use_iso_strokes:
            entities += '\t<!ENTITY ' + iso_stroke_entity   + ' "' + stroke_color   + '">\n'
    else:
        entities  = '\t<!ENTITY ' + stroke_entity + ' "' + default_stroke_color + '">\n'
        entities += '\t<!ENTITY ' + fill_entity   + ' "' + default_fill_color   + '">\n'
        if use_iso_strokes:
            entities += '\t<!ENTITY ' + iso_stroke_entity   + ' "' + default_stroke_color   + '">\n'

    #for simplicity, we simply replace the entire entity declaration block; this obviously would remove
    #any other custom entities declared within the SVG, but we assume that's an extreme edge case
    
    svgtext, n = re.subn(r'(<!DOCTYPE[^>\[]*)(\[[^\]]*\])*\>', r'\1 \n[\n' + entities + ']>\n', svgtext)

    #add a doctype if none already exists, adding the appropriate entities as well
    if n == 0:
        svgtext,n = re.subn("<svg", "<!DOCTYPE svg  PUBLIC '-//W3C//DTD SVG 1.1//EN'  'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd' [\n" + entities + "]>\n<svg", svgtext)
        if n == 0:
            sys.exit('Error: Could not insert entities into DTD')

#convert entities to references
stroke_entity = '&' + stroke_entity + ';'
fill_entity = '&' + fill_entity + ';'

#create the SVG DOM
try:
    svgxml = xml.dom.minidom.parseString(svgtext);
except Exception, e:
    sys.exit('Error: Could not parse ' + svgfilename + str(e))

#extract top level nodes
i = 0
svgindex = 0;
docindex = 0;
for element in svgxml.childNodes:
    if element.nodeType == 10:
        docindex = i;
    elif element.localName == 'svg':
        svgindex = i;
        break;
    i += 1;

doctype = svgxml.childNodes[docindex]
svg = svgxml.childNodes[svgindex]
icons = svg.childNodes;

#validate canvas size
w = svg.getAttribute('width')
h = svg.getAttribute('height')

if w != '55px' or h != '55px':
    print "Warning: invalid canvas size (%s, %s); Should be (55px, 55px)" % (w, h)

#define utility functions
def getStroke(node):    
    s = node.getAttribute('stroke')
    if s:
        return s.lower()
    else:
        if re.search(r'stroke:', node.getAttribute('style')):
            s = re.sub(r'.*stroke:\s*(#*[^;]*).*', r'\1', node.getAttribute('style'))
            return s.lower()
        else:
            return 'none'

def setStroke(node, value):
    s = node.getAttribute('stroke')
    if s:
        node.setAttribute('stroke', value)
    else:
        s = re.sub(r'stroke:\s*#*[^;]*', 'stroke:' + value,  node.getAttribute('style'))
        node.setAttribute('style', s)

def getFill(node):
    f = node.getAttribute('fill')
    if f:
        return f.lower()
    else:
        if re.search(r'fill:', node.getAttribute('style')):
            f = re.sub(r'.*fill:\s*(#*[^;]*).*', r'\1', node.getAttribute('style'))
            return f.lower()
        else:
            return 'none'
    
def setFill(node, value):
    f = node.getAttribute('fill')
    if f:
        node.setAttribute('fill', value)
    else:
        s = re.sub(r'fill:\s*#*[^;]*', 'fill:' + value,  node.getAttribute('style'))
        node.setAttribute('style', s)

def replaceEntities(node, indent=''):
    
    strokes_replaced = 0
    fills_replaced = 0

    if node.localName:
        str = indent + node.localName
    
    if node.nodeType == 1: #only element nodes have attrs
        
        #replace entities for matches
        if getStroke(node) == stroke_color:
            setStroke(node, stroke_entity)
            strokes_replaced += 1
        
        if getStroke(node) == fill_color:
            setStroke(node, fill_entity)
            strokes_replaced += 1
        
        if getFill(node) == fill_color:
            setFill(node, fill_entity)
            fills_replaced += 1
            
        if getFill(node) == stroke_color:
            setFill(node, stroke_entity)
            fills_replaced += 1
        
        str = str + " (" + getStroke(node) + ", " + getFill(node) + ")"
        if verbose:
            print str
            
    #recurse on DOM
    for n in node.childNodes:
        sr, fr = replaceEntities(n, indent + "   ")
        strokes_replaced += sr
        fills_replaced += fr

    #return the number of replacements made
    return (strokes_replaced, fills_replaced)

def fix_isolated_strokes(node):

    strokes_fixed = 0
    #recurse on DOM
    last_n = None
    for n in node.childNodes:
        sf = fix_isolated_strokes(n)
        strokes_fixed += sf

    if node.nodeType == 1: #only element nodes have attrs
        
        #find strokes with no associated fill
        if getStroke(node) != 'none' and getFill(node) == 'none':
            strokes_fixed += 1
            setStroke(node, "&iso_stroke_color;")
        
    #return the number of strokes fixed
    return strokes_fixed


#these functions attempt to guess the hex values for the stroke and fill entities

def getColorPairs(node, pairs=[]):

    if node.nodeType == 1:
        
        #skip masks
        if node.localName == 'mask':
            return pairs

        node_name = ''
        try:
            if creator == 'inkscape' and node.attributes.getNamedItem('inkscape:label'):
                node_name = node.attributes.getNamedItem('inkscape:label').nodeValue
            else:
                node_name = node.attributes.getNamedItem('id').nodeValue
        except:
            pass

        #skip the template layers
        if node_name.startswith('_'):
            return pairs

        pair = (getStroke(node), getFill(node))
        if pair[0] != pair[1]:
            pairs.append(pair)

    #recurse on DOM
    for n in node.childNodes:
        getColorPairs(n, pairs)

    return pairs

def guessEntities(node):

    guesses = getColorPairs(node)
    #print guesses

    stroke_guess = 'none'
    fill_guess = 'none'

    for guess in guesses:
        if stroke_guess == 'none':
            stroke_guess = guess[0]
        if fill_guess == 'none' and stroke_guess != guess[1]:
            fill_guess = guess[1]
        if guess[0] == fill_guess and guess[1] != 'none':
            fill_guess = stroke_guess
            stroke_guess = guess[0]
            if fill_guess == 'none':
                fill_guess = guess[1]

    return (stroke_guess, fill_guess)


#guess the entity values, if they aren't passed in

if use_entities:
    if entities_passed < 2:
        stroke_color, fill_color = guessEntities(svg)

    if confirm_guess or verbose:
        print '\nentity definitions:'
        print '     stroke_entity = ' + stroke_color
        print '     fill_entity = ' + fill_color

    if entities_passed < 2:
        if confirm_guess:
            response = raw_input("\nAre these entities correct? [y/n] ")
            if response.lower() != 'y':
                print 'Please run this script again, passing the proper colors with the -s and -f flags.'
                sys.exit(1)

#define the HTML for preview output

previewHTML = "\
<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\"\n\
\t\"http://www.w3.org/TR/html4/strict.dtd\">\n\
<html>\n\
<head>\n\
\t<meta http-equiv=\"Content-type\" content=\"text/html; charset=utf-8\">\n\
\t<title>Sugar Icon Preview: ~~~</title>\n\
\t<script type=\"text/javascript\" charset=\"utf-8\">\n\
\t\tvar bordered = false;\n\
\t\tvar bgcolor = \"#FFF\"\n\
\n\
\t\tfunction toggleIconBorder(reset)\n\
\t\t{\n\
\t\t\tif(!reset) bordered = !bordered;\n\
\t\t\t\n\
\t\t\tvar objects = document.getElementsByTagName('object')\n\
\t\t\tfor(var i = 0; i < objects.length; i++)\n\
\t\t\t{\n\
\t\t\t\tif(bordered) objects[i].style.border = 'solid 1px gray';\n\
\t\t\t\telse objects[i].style.border = 'solid 1px ' + bgcolor;\n\
\t\t\t}\n\
\t\t}\n\
\t\tfunction setBackgroundColor(color)\n\
\t\t{\n\
\t\t\tbgcolor = color;\n\
\t\t\tvar objects = document.getElementsByTagName('div');\n\
\t\t\tfor(var i = 0; i < objects.length; i++)\n\
\t\t\t\tif(objects[i].className == 'cell')\n\
\t\t\t\t\tobjects[i].style.backgroundColor = color;\n\
\t\t\t\n\
\t\t\ttoggleIconBorder(true)\n\
\t\t}\n\
\t</script>\n\
\t<style type=\"text/css\" media=\"screen\">\n\
\t\thtml, body {\n\
\t\t\tmargin: 0px;\n\
\t\t\tborder: 0px;\n\
\t\t\tbackground-color: white;\n\
\t\t\t\n\
\t\t\tfont: 14px Helvetica;\n\
\t\t\tcolor: gray;\n\
\t\t}\n\
\t\t.cell {\n\
\t\t\twidth: 57px;\n\
\t\t\theight: 57px;\n\
\t\t\tpadding: 8px;\n\
\t\t\tborder: solid 1px gray;\n\
\t\t}\n\
\t\t.icon {\n\
\t\t\tmargin: 0px;\n\
\t\t\tpadding: 0px;\n\
\t\t\tborder: solid 1px #FFF;\n\
\t\t\twidth: 55px;\n\
\t\t\theight: 55px;\n\
\t\t}\n\
\t\t#icons {\n\
\t\t\tmargin-top: 30px;\n\
\t\t}\n\
\n\
\t\t#icons > li {\n\
\t\t\tdisplay: block;\n\
\t\t\tmargin: 0px;\n\
\t\t\tmargin-bottom: 20px;\n\
\t\t}\n\
\t\t#description {\n\
\t\t\twidth: 300px;\n\
\t\t\tposition: absolute;\n\
\t\t\ttop: 0px;\n\
\t\t\tleft: 200px;\n\
\t\t\tborder-left: solid 1px gray;\n\
\t\t\tmargin-top: 30px;\n\
\t\t\tpadding-left: 30px;\n\
\t\t\tfont-size: 11px;\n\
\t\t}\n\
\t\t#description ul {\n\
\t\t\tmargin: 0px;\n\
\t\t\tpadding: 0px;\n\
\t\t\tdisplay: block;\n\
\t\t\tlist-style: square;\n\
\t\t}\n\
\t\tli { margin-bottom: 10px; }\n\
\t\ta, a:visited { color: gray; }\n\
\t\ta:hover { color: black; }\n\
\t</style>\n\
</head>\n\
<body>\n\
\t\t<ul id='icons'>\n\
\t\t<li><div class='cell'><object class='icon' id='stroke' data=\"~~~.stroke.svg\" type=\"image/svg+xml\"></object></div><br>stroke\n\
\t\t<li><div class='cell'><object class='icon' id='fill' data=\"~~~.fill.svg\" type=\"image/svg+xml\"></object></div><br>fill\n\
\t\t<li><div class='cell'><object class='icon' id='both' data=\"~~~.both.svg\" type=\"image/svg+xml\"></object></div><br>both\n\
\t\t</ul>\n\
\t\t<div id='description'>\n\
\t\t\t<h3>Icon Validation</h3>\n\
\t\t\t<ul>\n\
\t\t\t\t<li>Ensure that your icons appear to be centered within their boxes.\n\
\t\t\t\t\tIf they appear off-center or cropped, you may have created your icon on canvas other than the required 55px square.\n\
\t\t\t\t\tClick to <a href='javascript:toggleIconBorder();'>toggle</a> the 55px canvas border.\n\
\t\t\t\t<li>If your icon appears off-center but has the correct 55px canvas, it may simply have uneven visual balance.\n\
\t\t\t\t\tThis means, though it may be technically centered, differences in the distribution of \"mass\" cause it to appear otherwise.  \n\
\t\t\t\t\tTry shifting the icon slightly on your canvas, while ensuring that you don't accidentally exceed the 55px boundary.\n\
\t\t\t\t<!--li>Click to see your icon on <a href=\"javascript:setBackgroundColor('#000');\">black</a>, \n\
\t\t\t\t\t<a href=\"javascript:setBackgroundColor('#FFF');\">white</a>, <a href=\"javascript:setBackgroundColor('#282828');\">gray</a>.<!-->\n\
\t\t\t\t<li>Ensure that the first two icons appear entirely in gray, and that all of the third icon is colored blue and green, with the latter being the fill color.\n\
\t\t\t\t\tIf any fail to meet these requirements, your icon does not have proper stroke and/or fill entities defined.\n\
\t\t\t\t\tInvestigate the <b>-s</b> and <b>-f</b> options of sugar-iconify, and be sure that your input SVG doesn't have extra colors in its palette.\n\
\t\t\t\t<li>Ensure that your icon reads clearly when viewed only as strokes.\n\
\t\t\t\t\tThis visual style will be used to represent activities/objects which are inactive, or uninstantiated.\n\
\t\t\t\t\tConsider applying outlining strokes to any filled shapes that do not already have them.\n\
\t\t\t\t<li>Ensure that your icon reads clearly when viewed only as fills.\n\
\t\t\t\t\tThis visual style will be used for representing activity types within other icons, such as invitations, transfers, and objects.  \n\
\t\t\t\t\tIf you have strokes which are isolated from fills, neither outlining them nor sitting against a filled background, please \n\
\t\t\t\t\tinvestigate the <b>-i</b> option of the sugar-iconify script.\n\
\t\t\t</ul>\n\
\t\t\t<i>For more information, please see the OLPC wiki page on <a href='http://wiki.laptop.org/go/Making_Sugar_Icons' target='_blank'>making sugar icons</a>.</i>\n\
\t\t</div>\n\
</body>\n\
</html>\n\
"

#finally, do the icon conversion and export

if multiple:
    #export each icon as a separate file by top level group
    n_icons_exported = 0
    n_warnings = 0
    for icon in icons:
    
        try:
            #skip whitespace and unnamed icons
            if icon.localName == 'g' and icon.attributes:
            
                icon_name = ''
                try:
                    if creator == 'inkscape' and icon.attributes.getNamedItem('inkscape:label'):
                        icon_name = icon.attributes.getNamedItem('inkscape:label').nodeValue
                    else:
                        icon_name = icon.attributes.getNamedItem('id').nodeValue
                except:
                    pass        

                #skip the template layers
                if not icon_name.startswith('_'):
        
                    #skip non-matches
                    if pattern == '' or re.search(pattern, icon_name):

                        if verbose:
                            print '\nExporting ' + icon_name + '.svg...'
                        icon_xml = xml.dom.minidom.Document();
            
                        #construct the SVG
                        icon_xml.appendChild(doctype)
                        icon_xml.appendChild(svg.cloneNode(0))
            
                        icon_xml.childNodes[1].appendChild(icon) 
                        icon_xml.childNodes[1].childNodes[0].setAttribute('display', 'block')
            
                        if use_entities:
                            strokes_replaced, fills_replaced = replaceEntities(icon_xml.childNodes[1])
                
                            if not strokes_replaced and not fills_replaced:
                                print 'Warning: no entity replacements were made in %s' % icon_name
                            elif not strokes_replaced:
                                print 'Warning: no stroke entity replacements were made in %s' % icon_name
                            elif not fills_replaced:
                                print 'Warning: no fill entity replacements were made in %s' % icon_name

                            if not strokes_replaced or not fills_replaced:
                                n_warnings += 1
            
                        #write the file
                        try:
                            f = open(output_path + icon_name + '.svg', 'w')
                        except:
                            sys.exit('Error: Could not locate directory ' + output_path)
            
                        try:
                            #had to hack here to remove the automatic encoding of '&' by toxml() in entity refs
                            #I'm sure there is a way to prevent need for this if I knew the XML DOM better
                            icon_svgtext = icon_xml.toxml()
                            icon_svgtext = re.sub('&amp;', '&', icon_svgtext)
                            if not use_default_colors:
                                icon_svgtext = re.sub(r'ENTITY stroke_color "[^"]*"', r'ENTITY stroke_color "' + stroke_color  + '"', icon_svgtext)
                                icon_svgtext = re.sub(r'ENTITY fill_color "[^"]*"', r'ENTITY fill_color "' + fill_color  + '"', icon_svgtext)
                            f.write(icon_svgtext)
                            f.close()
                        except:
                            sys.exit('Error: Could not write file ' + icon_name + '.svg')
                        
                        n_icons_exported += 1
        except:
            #catch any errors we may have missed, so the rest of the icons can export normally
            if(icon_name):
                print 'Error: Could not export' + icon_name + '.svg'

    if verbose:
        if n_icons_exported == 1:
            print 'Successfully exported 1 icon' 
        else:
            print 'Successfully exported %d icons' % n_icons_exported
        
        if n_warnings == 1:
            print 'Warnings were reported for 1 icon'
        elif n_warnings > 1:
            print 'Warnings were reported for %d icons' % n_warnings

else:
    #output a single converted icon
    
    if not overwrite_input:
        outfilename = re.sub(r'(.*\.)([^.]+)', r'\1sugar.\2', svgfilename)
        if verbose:
            print 'Exporting ' + outfilename + ' ...'
    else:
        outfilename = svgfilename
        if verbose:
            print 'Overwriting ' + outfilename + ' ...'

    #remove the template layers
    for node in svg.childNodes:
        
        #only check named nodes
        if node.localName == 'g' and node.attributes:        
            try:
                if creator == 'inkscape' and node.attributes.getNamedItem('inkscape:label'):
                    node_name = node.attributes.getNamedItem('inkscape:label').nodeValue
                else:
                    node_name = node.attributes.getNamedItem('id').nodeValue

                if node_name.startswith('_'):
                    node.parentNode.removeChild(node)
            except:
                pass

    if use_entities:
        strokes_replaced, fills_replaced = replaceEntities(svgxml)
        if not strokes_replaced and not fills_replaced:
            print 'Warning: no entity replacements were made'
        elif not strokes_replaced:
            print 'Warning: no stroke entity replacements were made'
        elif not fills_replaced:
            print 'Warning: no fill entity replacements were made'

        if use_iso_strokes:
            strokes_fixed = fix_isolated_strokes(svgxml)
            if strokes_fixed > 0 and verbose:
                print "%d isolated strokes fixed" % strokes_fixed

    #create the output file(s)
    if output_examples:

        example_path = output_path + re.sub(r'(.*\.)([^.]+)', r'\1preview', svgfilename) + '/'
        try:
            os.mkdir(example_path)
        except:
            pass

        try:
            f = open(example_path + 'preview.html', 'w')
        except:
            print "Error: could not create HTML preview file"

        try:
            f.write(re.sub(r'~~~', svgbasename, previewHTML))
            f.close()
        except:
            sys.exit('Error: could not write to HTML preview file')

        example_colors = [(default_stroke_color, "#FFFFFF", default_stroke_color), 
                  ("#FFFFFF", default_stroke_color, default_stroke_color), 
                                  ("#0000AA", "#00DD00", "#0000AA")]
        example_filenames = [re.sub(r'(.*\.)([^.]+)', r'\1stroke.\2', svgfilename),
                     re.sub(r'(.*\.)([^.]+)', r'\1fill.\2', svgfilename),
                     re.sub(r'(.*\.)([^.]+)', r'\1both.\2', svgfilename) ]

        icon_svgtext = svgxml.toxml()
        icon_svgtext = re.sub('&amp;', '&', icon_svgtext)

        for i in range(0, len(example_filenames)):
            try:
                f = open(example_path + example_filenames[i], 'w')
            except:
                sys.exit('Error: Could not save to ' + example_path + example_filenames[i])
            try:
                icon_svgtext = re.sub(r'ENTITY stroke_color "[^"]*"', r'ENTITY stroke_color "' + example_colors[i][0]  + '"', icon_svgtext)
                icon_svgtext = re.sub(r'ENTITY fill_color "[^"]*"', r'ENTITY fill_color "' + example_colors[i][1]  + '"', icon_svgtext)
                if use_iso_strokes:
                    icon_svgtext = re.sub(r'ENTITY iso_stroke_color "[^"]*"', r'ENTITY iso_stroke_color "' + example_colors[i][2]  + '"', icon_svgtext)                    
                f.write(icon_svgtext)
                f.close()
            except:
                sys.exit('Error: Could not write file ' + output_path + example_filenames[i])

    try:
        f = open(output_path + outfilename, 'w')
    except:
        sys.exit('Error: Could not save to ' + output_path + outfilename)

    try:
        icon_svgtext = svgxml.toxml()
        icon_svgtext = re.sub('&amp;', '&', icon_svgtext)
        if not use_default_colors:
            icon_svgtext = re.sub(r'ENTITY stroke_color "[^"]*"', r'ENTITY stroke_color "' + stroke_color  + '"', icon_svgtext)
            icon_svgtext = re.sub(r'ENTITY fill_color "[^"]*"', r'ENTITY fill_color "' + fill_color  + '"', icon_svgtext)
            if use_iso_strokes:
                icon_svgtext = re.sub(r'ENTITY iso_stroke_color "[^"]*"', r'ENTITY iso_stroke_color "' + stroke_color  + '"', icon_svgtext)
        f.write(icon_svgtext)
        f.close()

    except:
        sys.exit('Error: Could not write file ' + output_path + outfilename)


