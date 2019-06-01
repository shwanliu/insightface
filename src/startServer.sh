
docker run \
	--name face_server \
	-v /Users/liuxiaoying/workplace/CV_Code/insightface:/opt/insightface \
	-v /opt/images:/opt/images \
	-p 5000:5000 \
	-e WORKERS=1 \
	-e THREADS=2 \
	-e PORT=5000 \
	-e PYTHONUNBUFFERED=0 \
	-d \
	face_server