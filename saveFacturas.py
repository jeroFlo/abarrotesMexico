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
        folio = xml_root.attrib['Folio']
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

##            except IOError:
##                try:
##
##                    os.mkdir("{}".format(df['rutaGuardarZips']))
##                    shutil.move("{}".format(zip.filename),"{}\{}.zip".format(df['rutaGuardarZips'],file_name))
##                    print("\n\t *** {} ***".format(zip.filename))
##                    print("\t Nuevo nombre: {}.zip".format(file_name))
##                    print("\t Ruta: {}".format(df['rutaGuardarZips']))
##                except WindowsError:
##                    print(" ERROR: la carpeta {} ya existe".format(df['rutaGuardarZips']))
##
##                #except:
#    print(" ERROR: contacta a tu programador")
# except:
#   print(" ERROR: contacta a tu programador")

'''
class Helper:
    def __init__(self, json_file):
        df = self._extractJson(json_file)
        self.zipsPath = df["rutaZips"]
        self.zipsSave = df["rutaGuardarZips"]
        self.filesSave = df["rutaGuardarArchivos"]
        self.numberAllowed = df["numeroArchivos"]

    def _extractJson(self, path_json):
        f = open(path_json)
        df = json.load(f)
        f.close()
        return df

class Invoice:
    def __init__(self, path_xml):
        self.xml_original_name = path_xml
        tree = etree.parse(path_xml)
        xml_root = tree.getroot()
        self.xml_tags_prefix = xml_root.tag.split('}')[0][1:]
        emisor_info = xml_root.find('{}{}{}Emisor'.format('{', xml_tags_prefix, '}'))
        self.emisor_rfc = emisor_info.attrib['Rfc']
        self.emisor_name = emisor_info.attrib['Nombre']
        date = xml_root.attrib['Fecha'].split('-')
        self.folio = xml_root.attrib['Folio']
        if self.emisor_rfc.upper() in ['DDI031219J69']:
            self.folio = 'XXXX'
        try:
            self.serie = xml_root.attrib['Serie']
            self.serie += '-'
        except:
            self.serie = ""
        self.year = date[0]
        self.month = date[1]
        self.day = date[2].split('T')[0]
        self.total = xml_root.attrib['Total']

    def __str__(self):
        file_name = f"{self.serie}{self.folio}__" \
                    f"{self.emisor_name.replace(' ', '_').capitalize()}__" \
                    f"{self.year}-{self.month}-{self.day}__" \
                    f"${self.total}"
        return file_name


    def formatName(self, ):
        pass

def main():
    info = Helper('datos.json')
    with os.scandir(info.zipsPath) as archi:
        for ar in archi:
            if ar.name.endswith(".zip") or ar.name.endswith(".ZIP"):
                test_file_name = ar.path
                with ZipFile(test_file_name, 'r') as zip:
                    print('-' * 70)
                    print(f"*** ZIP {zip.filename} ***")
                    zip.printdir()
                    files_in_zip = zip.namelist()
                    if len(files_in_zip) == info.numberAllowed:
                        for file_num in range(len(files_in_zip)):
                            if file_num % 2 == 0:
                                if not files_in_zip[file_num].casefold().endswith(".PDF"):
                                    break
                                generic_name = files_in_zip[file_num][:-4]
                                pdf_file = files_in_zip[file_num]
                            else:
                                if not files_in_zip[file_num].casefold().endswith('.XML') \
                                        and files_in_zip[file_num][:-4] != generic_name:
                                    print(f" ADVERTENCIA: EL XML  DE {generic_name} NO SE ENCUENTRA, NO SE PUEDE"
                                          "PROCESAR")
                                    continue
                                zip.extractall()
                                xml_file = files_in_zip[file_num]
                                try:
                                    factura = Invoice(xml_file)
                                except FileNotFoundError:
                                    print(f" *** El archivo {xml_file} no se encontro *** ")
                                    continue

                                try:
                                    print(f"\n\t ***  Archivo {xml_file} *** ")
                                    shutil.move(xml_file, f"{info.filesSave}\{factura}.xml")
                                    print(f"\t Nuevo nombre: {factura}.xml")
                                    print(f"\t Ruta: {info.filesSave}")
                                except FileExistsError:
                                    print(" ADVERTENCIA: YA EXISTE UN ARCHIVO CON EL MISMO NOMBRE")
                                except PermissionError:
                                    print(" ERROR: EL ARCHIVO ESTA ABIERTO POR OTRO PROGRAMA ")
                                except:
                                    print(" ERROR: contacta a tu programador")
                                try:
                                    print(f"\n\t ***  Archivo {pdf_file} *** ")
                                    shutil.move(pdf_file, f"{df['rutaGuardarArchivos']}\{factura}.pdf")
                                    print(f"\t Nuevo nombre: {factura}.pdf")
                                    print(f"\t Ruta: {df['rutaGuardarArchivos']}")
                                except FileExistsError:
                                    print(" ADVERTENCIA: YA EXISTE UN ARCHIVO CON EL MISMO NOMBRE")
                                except PermissionError:
                                    print(" ERROR: EL ARCHIVO ESTA ABIERTO POR OTRO PROGRAMA ")
                                except:
                                    print(" ERROR: contacta a tu programador")
                    else:
                        print(f" ADVERTENCIA: ESTE ZIP NO FUE PROCESADO PORQUE NO TENIA "
                              f"{info.numberAllowed} ARCHIVOS EN SU INTERIOR")
                        continue
                try:
                    shutil.move(f"{zip.filename}",
                                f"{info.zipsSave}\{factura}.zip")
                    # print(file_name)
                except FileNotFoundError:
                    try:
                        os.mkdir(f"{info.zipsSave}")
                        shutil.move(f"{zip.filename}",
                                    f"{info.zipsSave}\{factura}.zip")
                    except FileExistsError:
                        print(f" ERROR: la carpeta {info.zipsSave} ya existe")
                    except:
                        print(" ERROR: contacta a tu programador")
                except:
                    print(" ERROR: contacta a tu programador")

if __name__ == '__main__':
    main()
'''
