
-- where	φ1,λ1 is the start point, φ2,λ2 the end point (Δλ is the difference in longitude)
-- where	φ is latitude, λ is longitude, R is earth’s radius (mean radius = 6,371km);

JavaScript:	
var x = (λ2-λ1) * Math.cos((φ1+φ2)/2); Dlongitude -- DL
var y = (φ2-φ1); Dlatitude -- DF
var d = Math.sqrt(x*x + y*y) * R;

// more computational heavy
var R = 6371e3; // metres
var φ1 = lat1.toRadians();
var φ2 = lat2.toRadians();
var Δφ = (lat2-lat1).toRadians();
var Δλ = (lon2-lon1).toRadians();

var a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
        Math.cos(φ1) * Math.cos(φ2) *
        Math.sin(Δλ/2) * Math.sin(Δλ/2);
var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

var d = R * c;

select sqrt(df*df + dl*dl) * 6371e3 as dm, latitude, longitude  from (
select (cast(longitude as float)*pi()/180 - -117.72369671*pi()/180) * cos((cast(latitude as float)*pi()/180 + 33.57830762*pi()/180)/2) as dl,

(cast(latitude as float)*pi()/180 - 33.57830762*pi()/180) as df, latitude, longitude from spots

) 
-- where round(latitude,4) = 33.5783 and round(longitude,4)=-117.7237
order by  sqrt(df*df + dl*dl) * 6371e3 


select 6371e3*sqrt( (longitude - -117.72528409)*(longitude - -117.72528409) + (latitude-33.57830762)*(latitude-33.57830762)) from spots;