% This function converts an array of bytes of a png fine into an image
function img = png2image(b)
% decode image stream using Java
jImg = javax.imageio.ImageIO.read(java.io.ByteArrayInputStream(b));
h = jImg.getHeight;
w = jImg.getWidth;

% convert Java Image to MATLAB image
p = reshape(typecast(jImg.getData.getDataStorage, 'uint8'), [4,w,h]);
img = cat(3, ...
        transpose(reshape(p(4,:,:), [w,h])), ...
        transpose(reshape(p(3,:,:), [w,h])), ...
        transpose(reshape(p(2,:,:), [w,h])));

end 