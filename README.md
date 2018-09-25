
to compile 
mvn clean -gs .m2/settings.xml package

mvn clean -gs .m2/settings.xml -DskipTests package 

to run java 
java -jar ./target/Huhula-0.00001.jar -c .conf/defaults.conf -w -r /Users/ivasilchikov/spot

