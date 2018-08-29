#! /bin/bash
# makes the pipes for the lander modules to communicate

PIPES_DIRECTORY='/tmp/lander'

mkdir -p $PIPES_DIRECTORY

pipes=( calculatorFromControl calculatorToControl calculatorToAxes calculatorFromAxes )
for pipe in "${pipes[@]}" ; do
  echo "creating pipe $pipe"
  rm $PIPES_DIRECTORY/$pipe
  mkfifo $PIPES_DIRECTORY/$pipe
done

echo
ls -la $PIPES_DIRECTORY | grep prw
