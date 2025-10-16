% login by user 1 or 2
select='s1'; % s2
% temp image file name
formatofImage='png';
imagefile=[tempname,'.',formatofImage];

% load binary image from database ( db
% ( for example I am showing as a matfile)

data=load("signatureBinary.mat",select); % currently 2 signature image are there in this example

% write

if isdeployed==1
    makeDOMCompilable();
    import mlreportgen.report.*
    import mlreportgen.dom.*
else
    import mlreportgen.report.*
    import mlreportgen.dom.*
end

filename='testreport';
R=Report(filename,'pdf');
open(R);
c1=Chapter('userSignature');
add(c1,Paragraph)
text="Lab test conducted and verfied by";
add(c1,text)

switch select
    case "s1"
        imwrite(data.s1,imagefile); % user 1

    case "s2"
        imwrite((data.s2),imagefile); % user 2
    otherwise
end
sign=Image(imagefile);
%fix the image height and width
sign.Height='100px';
sign.Width='200px';
add(c1,sign); % add image to report/chapter
add(R,c1);
close(R);

% delete temp image
delete(imagefile);