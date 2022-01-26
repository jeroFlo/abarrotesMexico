from zipfile import ZipFile
import xml.etree.ElementTree as etree
import os
import json
import shutil

path_json = "datos.json"
f = open(path_json)
df = json.load(f)
f.close()

for ar in os.listdir(df['rutaZips']):
    if ar.endswith(".zip"):
        test_file_name = "{}{}".format(df['rutaZips'], ar)
        zip = ZipFile(test_file_name, 'r')
        print('-' * 70)
        print("*** ZIP {} ***".format(zip.filename))
        zip.printdir()
        files_in_zip = zip.namelist()
        if len(files_in_zip) == 2:
            if files_in_zip[0].upper().endswith('.XML'):
                xml_file = files_in_zip[0]
            elif files_in_zip[1].upper().endswith('.XML'):
                xml_file = files_in_zip[1]
            else:
                print(" *** No hay archivo XML en este ZIP *** ")

            if files_in_zip[0].upper().endswith('.PDF'):
                pdf_file = files_in_zip[0]
            elif files_in_zip[1].upper().endswith('.PDF'):
                pdf_file = files_in_zip[1]
            else:
                print(" *** No hay archivo PDF en este ZIP ***")
                continue
        else:
            print(" ADVERTENCIA: ESTE ZIP NO FUE PROCESADO PORQUE NO TENIA "
                  "2 ARCHIVOS EN SU INTERIR")
            continue
        zip.extractall()
        try:
            tree = etree.parse(xml_file)
        except FileNotFoundError:
            print(" *** El archivo {} no se encontro *** ".format(xml_file))
            continue
        xml_root = tree.getroot()
        xml_tags_prefix = xml_root.tag.split('}')[0][1:]
        # print(xml_tags_prefix)
        emisor_info = xml_root.find('{}{}{}Emisor'.format('{', xml_tags_prefix, '}'))
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
        file_name = "{}{}__{}__{}-{}-{}__${}".format(serie, folio,
                                                     emisor_info.attrib['Nombre'].replace(' ', '_').capitalize(), year,
                                                     month, day, total)
        try:
            print("\n\t ***  Archivo {} *** ".format(xml_file))
            shutil.move(xml_file, "{}\{}.xml".format(df['rutaGuardarArchivos'], file_name))
            print("\t Nuevo nombre: {}.xml".format(file_name))
            print("\t Ruta: {}".format(df['rutaGuardarArchivos']))
        except NameError:
            print(" ADVERTENCIA: YA EXISTE UN ARCHIVO CON EL MISMO NOMBRE")
        except PermissionError:
            print(" ERROR: EL ARCHIVO ESTA ABIERTO POR OTRO PROGRAMA ")
        except:
            print(" ERROR: contacta a tu programador")
        try:
            print("\n\t ***  Archivo {} *** ".format(pdf_file))
            shutil.move(pdf_file, "{}\{}.pdf".format(df['rutaGuardarArchivos'], file_name))
            print("\t Nuevo nombre: {}.pdf".format(file_name))
            print("\t Ruta: {}".format(df['rutaGuardarArchivos']))
        except NameError:
            print(" ADVERTENCIA: YA EXISTE UN ARCHIVO CON EL MISMO NOMBRE")
        except PermissionError:
            print(" ERROR: EL ARCHIVO ESTA ABIERTO POR OTRO PROGRAMA ")
        except:
            print(" ERROR: contacta a tu programador")

        ##            try:
        zip_filename = zip.filename
        zip.close()
        shutil.move("{}".format(zip_filename), "{}\{}.zip".format(df['rutaGuardarZips'], file_name))
        print("\n\t *** {} ***".format(zip_filename))
        print("\t Nuevo nombre: {}.zip".format(file_name))
        print("\t Ruta: {}".format(df['rutaGuardarZips']))

##            except IOError:
##                try:
##
##                    os.mkdir("{}".format(df['rutaGuardarZips']))
##                    for num in range(1000):
##                        pass
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
