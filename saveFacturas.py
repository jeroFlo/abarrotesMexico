from zipfile import ZipFile
import xml.etree.ElementTree as etree
import os
import json
import shutil

path_json = "datos.json"
f = open(path_json)
df = json.load(f)
f.close()

if __name__ == "__main__":
    available_files = os.listdir(df['rutaZips'])
    xml_files = []
    pdf_files = []
    zip_files = []
    zip_content = {}
    while available_files:  # mientras la lista tenga elementos
        file = available_files.pop()
        if file.endswith('.xml'):
            xml_files.append(file[:-4])
        elif file.endswith('.pdf'):
            pdf_files.append(file[:-4])
        elif file.endswith('.zip'):
            zip_files.append(file)
            test_file_name = "{}\{}".format(df['rutaZips'], file)
            zip = ZipFile(test_file_name, 'r')
            # print("*** ZIP {} ***".format(zip.filename))
            #zip.printdir() # imprime el contenido del zip
            files_in_zip = zip.namelist()
            available_files.extend(files_in_zip)
            zip_content[tuple(files_in_zip)] = file
            zip.close()

    selected_files = list(set(xml_files) & set(pdf_files))
    num = 0
    is_found = False
    while selected_files:
        file = selected_files.pop()
        xml_file = "{}\{}.xml".format(df['rutaZips'], file)
        if not is_found:
            zip_filename = None
        try:
            tree = etree.parse(xml_file)
        except:
            for _zip_files, zip_name in zip_content.items():
                if "{}.xml".format(file) in _zip_files:
                    test_file_name = "{}\{}".format(df['rutaZips'], zip_name)
                    zip = ZipFile(test_file_name, 'r')
                    zip.extractall(path=df['rutaZips'])
                    zip_filename = zip.filename
                    zip.close()
                    selected_files.append(file)
                    zip_content.pop(_zip_files)
                    is_found = True
                    break
            if not is_found:
                print(" *** Los archivos con nombre {} no se encontraron *** ".format(file))
            continue
        is_found = False
        xml_root = tree.getroot()
        xml_tags_prefix = xml_root.tag.split('}')[0][1:]
        # print(xml_tags_prefix)
        emisor_info = xml_root.find('{}{}{}Emisor'.format('{', xml_tags_prefix, '}'))
        receptor_info = xml_root.find('{}{}{}Receptor'.format('{', xml_tags_prefix, '}'))
        uso_cfdi = receptor_info.attrib['UsoCFDI']
        if uso_cfdi == 'G02':
            tipo_fact = 'nc'
        else:
            tipo_fact = ''
        # print(emisor_info.attrib)
        emisor_rfc = emisor_info.attrib['Rfc']
        try:
            folio = xml_root.attrib['Folio']
        except KeyError:
            xtra_msg = "ERROR: este archivo no tiene Folio conocido {} se tomara el UUID".format(file)
            complemento_info = xml_root.find('{}{}{}Complemento'.format('{', xml_tags_prefix, '}'))
            was_found = False
            folio = 'XXXX'
            for child in complemento_info:
                print(child.tag,   child.attrib)
                for field, value in child.attrib.items():
                    if 'UUID' in field:
                        folio = value
                        was_found = True
                        break
                if was_found:
                    break

        if emisor_rfc.upper() in ['DDI031219J69']:
            folio = 'XXXX'
        fecha = xml_root.attrib['Fecha'].split('-')
        try:
            serie = xml_root.attrib['Serie']
            serie += '-'
        except:
            serie = ""
        year = fecha[0]
        month = fecha[1]
        day = fecha[2].split('T')[0]
        total = xml_root.attrib['Total']
        file_name = "{}{}__{}__{}-{}-{}_{}_${}".format(serie, folio,
                                                     emisor_info.attrib['Nombre'].replace(' ', '_').capitalize(), year,
                                                     month, day, tipo_fact, total)
        num += 1
        print('-'*70)
        print("{}. Archivos procesados correctamente: ".format(num))
        for file_type in ['.xml', '.pdf']:
            _file = "{}\{}{}".format(df['rutaZips'], file, file_type)
            try:
                print("\n\t ***  Archivo {} *** ".format(_file))
                shutil.move(_file, "{}\{}{}".format(df['rutaGuardarArchivos'], file_name, file_type))
                print("\t Nuevo nombre: {}{}".format(file_name, file_type))
                print("\t Nueva ubicacion: {}".format(df['rutaGuardarArchivos']))
            except NameError:
                print(" ADVERTENCIA: YA EXISTE UN ARCHIVO CON EL MISMO NOMBRE")
            except PermissionError:
                print(" ERROR: EL ARCHIVO ESTA ABIERTO POR OTRO PROGRAMA ")

        if zip_filename is not None:
            shutil.move("{}".format(zip_filename), "{}\{}.zip".format(df['rutaGuardarZips'], file_name))
            print("\n\t *** {} ***".format(zip_filename))
            print("\t Nuevo nombre: {}.zip".format(file_name))
            print("\t Nueva ubicacion: {}".format(df['rutaGuardarZips']))


