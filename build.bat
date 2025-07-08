@echo off
echo Copying package 'unbiasedupdates' into lambdas folder...

xcopy /E /I /Y unbiasedupdates lambdas\newsscrapingandfeed_BBC_AJ\unbiasedupdates

echo Copying requirements.txt into lambdas folder...
copy /Y requirements.txt lambdas\newsscrapingandfeed_BBC_AJ