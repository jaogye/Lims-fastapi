% This function validates if a row a table has dependencies (children)
function msgerror = checkChildren(conn, table, id )
msgerror ={} ; 
id = string(id) ; 
  switch table
      case 'Product'
          idchild = checkFK( conn,"SELECT id FROM sample WHERE product_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table Sample." , [id, table  ] ) ;
             return 
          end

          idchild = checkFK( conn,"SELECT id FROM spec WHERE typespec = 'GEN' and product_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table Spec." , [id, table  ] ) ;
          end     
          idchild = checkFK( conn,"SELECT id FROM spec WHERE typespec = 'CLI' and product_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table ClientList." , [id, table  ] ) ;
          end

          idchild = checkFK( conn,"SELECT id FROM samplematrix WHERE product_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table SampleMatrix." , [id, table  ] ) ;
          end

          idchild = checkFK( conn,"SELECT id FROM Map WHERE product_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table Map." , [id, table  ] ) ;
          end

      case 'SamplePoint'
          idchild = checkFK( conn,"SELECT id FROM sample WHERE samplepoint_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table Sample." , [id, table  ] ) ;
             return 
          end

          idchild = checkFK( conn,"SELECT id FROM samplematrix WHERE samplepoint_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table SampleMatrix." , [id, table  ] ) ;
          end
          
      case 'Quality'

          idchild = checkFK( conn,"SELECT id FROM sample WHERE quality_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table Sample." , [id, table  ] ) ;
             return 
          end

          idchild = checkFK( conn,"SELECT id FROM spec WHERE typespec = 'GEN' and quality_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table Spec." , [id, table  ] ) ;
          end
          idchild = checkFK( conn,"SELECT id FROM spec WHERE typespec = 'CLI' and quality_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table ClientList." , [id, table  ] ) ;
          end

          idchild = checkFK( conn,"SELECT id FROM samplematrix WHERE quality_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table SampleMatrix." , [id, table  ] ) ;
          end

          idchild = checkFK( conn,"SELECT id FROM Map WHERE quality_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table Map." , [id, table  ] ) ;
          end
          
      case 'SampleMatrix'
          idchild = checkFK( conn,"SELECT id FROM sample WHERE samplematrix_id =%s ",  id  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table Sample." , [id, table  ] ) ;
             return 
          end

      case 'Spec'
          idproduct = checkFK( conn,"SELECT product_id FROM spec WHERE typespec = 'GEN' and id =%s ",  id  ) ; 
          idchild = checkFK( conn,"SELECT id FROM spec WHERE typespec = 'CLI' and product_id =%s ",  idproduct  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table ClientList via Product id %s." , [id, table, idproduct  ] ) ;
          end

          idchild = checkFK( conn,"SELECT id FROM samplematrix WHERE product_id =%s ",  idproduct  ) ; 
          if idchild > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table SampleMatrix via Product id %s." , [id, table, idproduct  ] ) ;
          end          

      case 'Variable'
          iddspec = checkFK( conn,"SELECT  variable_id id FROM dspec WHERE variable_id =%s ",  id  ) ;           
          if iddspec > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table dSpec via variable id %s." , [id, table, iddspec  ] ) ;
          end

          idlistvalue = checkFK( conn,"SELECT id, variable_id FROM listvalue WHERE variable_id =%s ",  id  ) ;           
          if idlistvalue > 0
             msgerror{ length(msgerror)+1 } = sprintf( "Action D.The id=%s of table %s have dependencies in table listvalue via variable id %s." , [id, table, idlistvalue  ] ) ;
          end

      case 'Listvalue'          
          T = select(conn, sprintf( "SELECT id, variable, listvalue " + ...
              " FROM measurement WHERE listvalue_id =%s ",  id  ) ) ; 
          if height(T) > 0
             variable = T.variable(1) ;
             variable = strtrim( variable{1} ); 
             listvalue = T.listvalue(1) ; 
             listvalue = strtrim( listvalue{1} ); 
             msgerror{ length(msgerror)+1 } = sprintf( "The value %s of variable %s have dependencies in table measurement. This value was not eliminated." , ...
                   listvalue, variable  ) ;
          end
          
  end


end
