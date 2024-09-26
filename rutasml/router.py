from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os #Para saber la ubicacion o el PATH
import pandas as pd

#Instacia
router = APIRouter()

class RespondeBody(BaseModel):
    message:str

class DataRequest(BaseModel):
    segundos: float
    etiqueta: str

bvh_files_path = "/src/BVH-files/Agradecimiento"
bvh_files_path_post = "/src/BVH-files"

src_path = "src"

ruta_actual = os.getcwd() #Aqui obtengo la ruta en donde me encuentro en este momento

#Acceso mediante: /rutasinofuente/base
@router.get("/base") #Endpoint base
def comprobacion():
    return {"mensaje": "Estas ruteando correctamente"}

#Acceso mediante: /rutasinofuente/ruta-actual
@router.get("/ruta-actual")
def fun_ruta_actual():
    return {f"mensaje: {ruta_actual}"}

#------------------------------------------------------------------------------------------
#A continuacion empezamos con lo que podria ser nuestra Aplicacion
@router.get("/watch-file")
async def give_file_bvh():
    ruta_archivo_BVH = ruta_actual + bvh_files_path
    #ruta_actual = /Users/kevininofuente/Documents/CERTUS/Gestion-de-Servicios-Cloud/Sesion-4-26-Setiembre/Sesion-4-API-Completa
    #bvh_files_path = /src/BVH-files/Agradecimiento_1.bvh
    return FileResponse(ruta_archivo_BVH)

@router.get("/get-file")
async def download_file_bvh():
    #ruta_actual = /Users/kevininofuente/Documents/CERTUS/Gestion-de-Servicios-Cloud/Sesion-4-26-Setiembre/Sesion-4-API-Completa
    #bvh_files_path = /src/BVH-files/Agradecimiento
    k=3
    ruta_archivo_BVH = ruta_actual + bvh_files_path + "_" + f"{k}" + ".bvh"
    return FileResponse(ruta_archivo_BVH, media_type="application/octet-stream", filename="archivo_de_animacion.bvh")

def encontrar_audio_mas_cercano(audio_data, etiqueta, duracion_objetivo):

    #Filtrar audios por etiqueta comparando solo la parte antes del subguion
    audio_data['etiqueta_simple'] = audio_data['filename'].str.split('_').str[0]
    audio_filtrados = audio_data[audio_data['etiqueta_simple'] == etiqueta]

    if audio_filtrados.empty:
        return None
    
    #Encontrar la duración más cercana a la duración objetivo
    audio_filtrados['diferencia'] = (audio_filtrados['duration'] - duracion_objetivo).abs()
    audio_mas_cercano = audio_filtrados.loc[audio_filtrados['diferencia'].idxmin()]

    return audio_mas_cercano['filename']

@router.post("give-data")
async def fun_obtener_datos(peticion: DataRequest):

    audio_durations_path = 'CSV-MP3-Segundos/audio_durations_sorted_agruped.csv'
    audio_durations_path_join = os.path.join(ruta_actual, src_path, audio_durations_path)

    #Leer el archivo CSV
    audio_data = pd.read_csv(audio_durations_path_join)

    #Obtener parámetros de la petición
    Etiqueta = peticion.etiqueta
    Segundos = peticion.segundos

    #Encontrar el nombre del audio más cercano
    nombre_audio_mas_cercano = encontrar_audio_mas_cercano(audio_data, Etiqueta, Segundos)

    if not nombre_audio_mas_cercano:
        raise HTTPException(status_code=404, detail="No se encontraton audios para los Segundos datos")
    
    ruta_archivo_BVH = os.path.joint(ruta_actual, bvh_files_path, f"{nombre_audio_mas_cercano}.bvh")

    if not os.path.exists(ruta_archivo_BVH):
        raise HTTPException(status_code=404, detail="No se encontraron BVH para la Etiqueta dada")
    
    return FileResponse(ruta_archivo_BVH, media_type="application/octet-stream", filename=f"{nombre_audio_mas_cercano}.bvh")