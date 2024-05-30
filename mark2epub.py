import markdown
import os
from xml.dom import minidom
import zipfile
import sys
import json

## markdown version 3.1

'''
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('ggplot')

X = np.linspace(-5,5,100)
Y = np.sin(X)+0.2*np.random.randn(100)
Z = -0.2*X

plt.figure(figsize=(8,5))
plt.scatter(X,Y,c="darkgray",s=50)
plt.plot(X,Z,linewidth=5,c="black")
plt.savefig("./a.png",dpi=150)
plt.show()
'''

def get_all_filenames(the_dir,extensions=[]):
    all_files = [x for x in os.listdir(the_dir)]
    all_files = [x for x in all_files if x.split(".")[-1] in extensions]

    return all_files


def get_packageOPF_XML(md_filenames=[],image_filenames=[],css_filenames=[],description_data=None):

    doc = minidom.Document()

    package = doc.createElement('package')
    package.setAttribute('xmlns',"http://www.idpf.org/2007/opf")
    package.setAttribute('version',"3.0")
    package.setAttribute('xml:lang',"en")
    package.setAttribute("unique-identifier","pub-id")

    ## Now building the metadata

    metadata = doc.createElement('metadata')
    metadata.setAttribute('xmlns:dc', 'http://purl.org/dc/elements/1.1/')

    for k,v in description_data["metadata"].items():
        if len(v):
            x = doc.createElement(k)
            for metadata_type,id_label in [("dc:title","title"),("dc:creator","creator"),("dc:identifier","book-id")]:
                if k==metadata_type:
                    x.setAttribute('id',id_label)
            x.appendChild(doc.createTextNode(v))
            metadata.appendChild(x)


    ## Now building the manifest

    manifest = doc.createElement('manifest')

    ## TOC.xhtml file for EPUB 3
    x = doc.createElement('item')
    x.setAttribute('id',"toc")
    x.setAttribute('properties',"nav")
    x.setAttribute('href',"TOC.xhtml")
    x.setAttribute('media-type',"application/xhtml+xml")
    manifest.appendChild(x)

    ## Ensure retrocompatibility by also providing a TOC.ncx file
    x = doc.createElement('item')
    x.setAttribute('id',"ncx")
    x.setAttribute('href',"toc.ncx")
    x.setAttribute('media-type',"application/x-dtbncx+xml")
    manifest.appendChild(x)

    x = doc.createElement('item')
    x.setAttribute('id',"titlepage")
    x.setAttribute('href',"titlepage.xhtml")
    x.setAttribute('media-type',"application/xhtml+xml")
    manifest.appendChild(x)

    for i,md_filename in enumerate(md_filenames):
        x = doc.createElement('item')
        x.setAttribute('id',"s{:05d}".format(i))
        x.setAttribute('href',"s{:05d}-{}.xhtml".format(i,md_filename.split(".")[0]))
        x.setAttribute('media-type',"application/xhtml+xml")
        manifest.appendChild(x)

    for i,image_filename in enumerate(image_filenames):
        x = doc.createElement('item')
        x.setAttribute('id',"image-{:05d}".format(i))
        x.setAttribute('href',"images/{}".format(image_filename))
        if "gif" in image_filename:
            x.setAttribute('media-type',"image/gif")
        elif "jpg" in image_filename:
            x.setAttribute('media-type',"image/jpeg")
        elif "jpeg" in image_filename:
            x.setAttribute('media-type',"image/jpg")
        elif "png" in image_filename:
            x.setAttribute('media-type',"image/png")
        if image_filename==description_data["cover_image"]:
            x.setAttribute('properties',"cover-image")

            ## Ensure compatibility by also providing a meta tag in the metadata
            y = doc.createElement('meta')
            y.setAttribute('name',"cover")
            y.setAttribute('content',"image-{:05d}".format(i))
            metadata.appendChild(y)
        manifest.appendChild(x)

    for i,css_filename in enumerate(css_filenames):
        x = doc.createElement('item')
        x.setAttribute('id',"css-{:05d}".format(i))
        x.setAttribute('href',"css/{}".format(css_filename))
        x.setAttribute('media-type',"text/css")
        manifest.appendChild(x)

    ## Now building the spine

    spine = doc.createElement('spine')
    spine.setAttribute('toc', "ncx")

    x = doc.createElement('itemref')
    x.setAttribute('idref',"titlepage")
    x.setAttribute('linear',"yes")
    spine.appendChild(x)
    for i,md_filename in enumerate(all_md_filenames):
        x = doc.createElement('itemref')
        x.setAttribute('idref',"s{:05d}".format(i))
        x.setAttribute('linear',"yes")
        spine.appendChild(x)

    guide = doc.createElement('guide')
    x = doc.createElement('reference')
    x.setAttribute('type',"cover")
    x.setAttribute('title',"Cover image")
    x.setAttribute('href',"titlepage.xhtml")
    guide.appendChild(x)


    package.appendChild(metadata)
    package.appendChild(manifest)
    package.appendChild(spine)
    package.appendChild(guide)
    doc.appendChild(package)

    return doc.toprettyxml()


def get_container_XML():
    container_data = """<?xml version="1.0" encoding="UTF-8" ?>\n"""
    container_data += """<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n"""
    container_data += """<rootfiles>\n"""
    container_data += """<rootfile full-path="OPS/package.opf" media-type="application/oebps-package+xml"/>\n"""
    container_data += """</rootfiles>\n</container>"""

    return container_data


def get_coverpage_XML(cover_image_path):
    ## Returns the XML data for the coverpage.xhtml file

    all_xhtml = """<?xml version="1.0" encoding="utf-8"?>\n"""
    all_xhtml += """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n"""
    all_xhtml += """<head>\n</head>\n<body>\n"""
    all_xhtml += """<img src="images/{}" style="height:100%;max-width:100%;"/>\n""".format(cover_image_path)
    all_xhtml += """</body>\n</html>"""

    return all_xhtml

def get_TOC_XML(default_css_filenames,markdown_filenames):
    ## Returns the XML data for the TOC.xhtml file

    toc_xhtml = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    toc_xhtml += """<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">\n"""
    toc_xhtml += """<head>\n<meta http-equiv="default-style" content="text/html; charset=utf-8"/>\n"""
    toc_xhtml += """<title>Contents</title>\n"""

    for css_filename in default_css_filenames:
        toc_xhtml += """<link rel="stylesheet" href="css/{}" type="text/css"/>\n""".format(css_filename)

    toc_xhtml += """</head>\n<body>\n"""
    toc_xhtml += """<nav epub:type="toc" role="doc-toc" id="toc">\n<h2>Contents</h2>\n<ol epub:type="list">"""
    for i,md_filename in enumerate(markdown_filenames):
        toc_xhtml += """<li><a href="s{:05d}-{}.xhtml">{}</a></li>""".format(i,md_filename.split(".")[0],md_filename.split(".")[0])
    toc_xhtml += """</ol>\n</nav>\n</body>\n</html>"""

    return toc_xhtml

def get_TOCNCX_XML(markdown_filenames):
    ## Returns the XML data for the TOC.ncx file

    toc_ncx = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    toc_ncx += """<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" xml:lang="fr" version="2005-1">\n"""
    toc_ncx += """<head>\n</head>\n"""
    toc_ncx += """<navMap>\n"""
    for i,md_filename in enumerate(markdown_filenames):
        toc_ncx += """<navPoint id="navpoint-{}">\n""".format(i)
        toc_ncx += """<navLabel>\n<text>{}</text>\n</navLabel>""".format(md_filename.split(".")[0])
        toc_ncx += """<content src="s{:05d}-{}.xhtml"/>""".format(i,md_filename.split(".")[0])
        toc_ncx += """ </navPoint>"""
    toc_ncx += """</navMap>\n</ncx>"""

    return toc_ncx

def get_chapter_XML(md_filename,css_filenames):
    ## Returns the XML data for a given markdown chapter file, with the corresponding css chapter files

    with open(os.path.join(work_dir,md_filename),"r",encoding="utf-8") as f:
        markdown_data = f.read()
    html_text = markdown.markdown(markdown_data,
                                  extensions=["codehilite","tables","fenced_code","footnotes"],
                                  extension_configs={"codehilite":{"guess_lang":False}}
                                  )

    all_xhtml = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    all_xhtml += """<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">\n"""
    all_xhtml += """<head>\n<meta http-equiv="default-style" content="text/html; charset=utf-8"/>\n"""


    for css_filename in css_filenames:
        all_xhtml += """<link rel="stylesheet" href="css/{}" type="text/css"/>\n""".format(css_filename)

    all_xhtml += """</head>\n<body>\n"""

    all_xhtml += html_text
    all_xhtml += """\n</body>\n</html>"""

    return all_xhtml

if __name__ == "__main__":
    if len(sys.argv[1:])<2:
        print("\nUsage:\n    python md2epub.py <markdown_directory> <output_file.epub>")
        exit(1)


    work_dir = sys.argv[1]
    output_path = sys.argv[2]

    images_dir = os.path.join(work_dir,r'images/')
    css_dir = os.path.join(work_dir,r'css/')

    ## Reading the JSON file containing the description of the eBook
    ## and compiling the list of relevant Markdown, CSS, and image files

    with open(os.path.join(work_dir,"description.json"),"r") as f:
        json_data = json.load(f)

    all_md_filenames=[]
    all_css_filenames=json_data["default_css"][:]
    for chapter in json_data["chapters"]:
        if not chapter["markdown"] in all_md_filenames:
            all_md_filenames.append(chapter["markdown"])
        if len(chapter["css"]) and (not chapter["css"] in all_css_filenames):
            all_css_filenames.append(chapter["css"])
    all_image_filenames = get_all_filenames(images_dir,extensions=["gif","jpg","jpeg","png"])

    ######################################################
    ## Now creating the ePUB book

    with zipfile.ZipFile(output_path, "w" ) as myZipFile:

        ## First, write the mimetype
        myZipFile.writestr("mimetype","application/epub+zip", zipfile.ZIP_DEFLATED )

        ## Then, the file container.xml which just points to package.opf
        container_data = get_container_XML()
        myZipFile.writestr("META-INF/container.xml",container_data, zipfile.ZIP_DEFLATED )

        ## Then, the package.opf file itself
        package_data = get_packageOPF_XML(md_filenames=all_md_filenames,
                                          image_filenames=all_image_filenames,
                                          css_filenames=all_css_filenames,
                                          description_data=json_data
                                         )
        myZipFile.writestr("OPS/package.opf",package_data, zipfile.ZIP_DEFLATED)

        ## First, we create the cover page
        coverpage_data = get_coverpage_XML(json_data["cover_image"])
        myZipFile.writestr("OPS/titlepage.xhtml",coverpage_data.encode('utf-8'),zipfile.ZIP_DEFLATED)

        ## Now, we are going to convert the Markdown files to xhtml files
        for i,chapter in enumerate(json_data["chapters"]):
            chapter_md_filename = chapter["markdown"]
            chapter_css_filenames = json_data["default_css"][:]
            if len(chapter["css"]):
                chapter_css_filenames.append(chapter["css"])

            chapter_data = get_chapter_XML(chapter_md_filename,chapter_css_filenames)
            myZipFile.writestr("OPS/s{:05d}-{}.xhtml".format(i,chapter_md_filename.split(".")[0]),
                               chapter_data.encode('utf-8'),
                               zipfile.ZIP_DEFLATED)


        ## Writing the TOC.xhtml file
        toc_xml_data = get_TOC_XML(json_data["default_css"],all_md_filenames)
        myZipFile.writestr("OPS/TOC.xhtml",toc_xml_data.encode('utf-8'),zipfile.ZIP_DEFLATED)

        ## Writing the TOC.ncx file
        toc_ncx_data = get_TOCNCX_XML(all_md_filenames)
        myZipFile.writestr("OPS/toc.ncx",toc_ncx_data.encode('utf-8'),zipfile.ZIP_DEFLATED)

        ## Copy image files
        for i,image_filename in enumerate(all_image_filenames):
            with open(os.path.join(images_dir,image_filename),"rb") as f:
                filedata = f.read()
            myZipFile.writestr("OPS/images/{}".format(image_filename),
                               filedata,
                               zipfile.ZIP_DEFLATED)

        ## Copy CSS files
        for i,css_filename in enumerate(all_css_filenames):
            with open(os.path.join(css_dir,css_filename),"rb") as f:
                filedata = f.read()
            myZipFile.writestr("OPS/css/{}".format(css_filename),
                               filedata,
                               zipfile.ZIP_DEFLATED)

    print("eBook creation complete")
