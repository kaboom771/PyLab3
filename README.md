команды для докера
создание образа: docker build -t lab3 .
сборка контейнера: docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw lab3
