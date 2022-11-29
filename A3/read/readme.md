We wrok in grayscale
First we use dilation and erosion to remove stray lines. The stray lines are removed after this step and the letters are restored to roughly the same state.
The image after this operatio is shown here.

The next morphological transformation essentially works to separate the margins and bold them using a morphological kernel. The image after this operation is shown here.

Observe the above image. The white parts of the  image can be viewed as a set of connected components. We can again see that turning the outermost connected component black will separate out the letters. Owing to thee small size of the letters in comaprison to the overall image this component will also be the largest one. So now our aim is to find the largest connected component in the image.

This simply performed by using an opencv function that computes the connected components of the image along wih some metadata. We use 8 connectivity to define the connectivity of two pixels. This is essentially a strong notion of connectivity that does not allow two sections to be connected if they are only linked at a corner.

The image now looks like this.

Observe that we have mostly segmented out the letters. Now we just want to remove the random white splotches.
All these splotches are essentially contours. So we get the contours and their hierarchy. contours can be organzed into a tree. The contours enclosed by a contour are its children. 

First we include only the highest level contours ( only the roots or children of the roots ). This is to remove the problem of letters like O or Theta which have multiple levels of elliptical contours and we only want the first two levels.

We can also see that the useful contours tend to be close to polygonal in shape. So we first approximate the contour with a suitable polygon which is defined at runtime using the contour charateristics, and compare the areas of the approximation and the original contours. If the areas are very close it means that the contour is useful because useful contours tend to be very well approximated by polygons in our use case. But we do not reject the contour if that is not the case.

Now we will finally check and remove the tiny splotches. We sort the remaining contours by area.
We then proceed in descending order. If the ratio of areas of two successive contours is too high, then we atop the traversal and reject the rest of the contours. The traversed contours are accepted. 

All of the accepted contours till now are drawn on an image.
An example is here.

Splitting an image into three parts is simple. We randomly sample N pooints and store the white pixels. Then we sort them on their x coordinates. We will see two large jumps in the x-coordinates. We plit the pixels at those two points. Thus we have three groups of pixels. We compute the average for all three groups. Then we take a square centered at the average for all three groups.