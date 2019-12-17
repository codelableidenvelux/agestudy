## this file constructs a table for the PsyToolkit code of the Corsi
## task. In short, for each line, there are:

## 1) the positions of 9 randomly positioned rectangles

## 2) the positions of 9 highlighted rectangles (basically the same as
## the first 9, but in the order of the to be memorized sequence

## 3) The numbers of the stimuli (1-9)

## Note: The difficulty of this code is to create 9 rectangles that do
## not overlap. We work with a 800x600 pixel area, rectanlges of
## 100x100 pixels, and the bottom right position is taken by a
## stimulus already (the done button)

## you need to save the produced output (lines of numbers) to a table
## file to be included in the PsyToolkit code

######################################################################

## a function to check if two rectangles overlap
## x1,y1=middle of rect of size w x h

rectoverlap = function( x1 , y1 , x2 , y2 , w , h ){
    Xoverlap = TRUE
    if ( ( x1 <= x2 & (x1+w/2)<(x2-w/2) )|
        ( x1 >  x2 & (x2+w/2)<(x1-w/2) )){
        Xoverlap = FALSE
    }

    Yoverlap = TRUE
    if ( ( y1 <= y2 & (y1+h/2)<(y2-h/2) )|
        ( y1 >  y2 & (y2+h/2)<(y1-h/2) )){
        Yoverlap = FALSE
    }

    if ( Xoverlap == TRUE & Yoverlap == TRUE ){
        Overlap = TRUE
    }else{Overlap = FALSE }
    return(Overlap)
}

## a function to check is a new rectanlge (xpos,ypos) would possibly
## overlap with one of the existing ones (as defined in arrays x,y)

checkoverlap = function(xpos,ypos,i,x,y,w,h){
    overlap = F
    for ( k in 1:i ){
        if ( rectoverlap( xpos,ypos,x[k],y[k] ,w,h) == T ){overlap = T}
    }

    ## the line for the "done button", that is, a bottom right
    ## location where no block should be placed
    if ( rectoverlap(xpos,ypos,750,550,w,h) == T){overlap=T}

    return( overlap )
}

for ( trials in 1:500 ){

    x = numeric(9)
    y = numeric(9)
    w = 100
    h = 100
    
    x[1] = sample(50:750,1)
    y[1] = sample(50:550,1)
    
    for ( i in 2:9 ){
        xpos = sample(50:750,1)
        ypos = sample(50:550,1)
        while( checkoverlap( xpos , ypos , i , x , y , w , h ) == TRUE ){
            xpos = sample(50:750,1)
            ypos = sample(50:550,1)
        }
        x[i] = xpos ; y[i] = ypos
    }
    
    ## select random sequence 1-9
    
    s = sample(1:9)
    
    ## plot(type="n",0,0,xlim=c(0,800),ylim=c(0,600))
    ## for( i in 1:9 ){
    ##     rect( x[i]-w/2,y[i]+h/2,x[i]+w/2,y[i]-h/2,col="red")
    ## }
    
    ## now write
    
    for( i in 1:9 ){
        cat( x[i] , " ", y[i] , " ")
    }
    
    for ( i in s ){
        cat( x[i] , " ", y[i] , " ")
    }
    
    for ( i in s ){
        cat( i , " ")
    }
    
    cat("\n")
}
