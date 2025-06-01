import cytoscape from 'cytoscape';
// Import from shared utility - initialization happens in this file
import '../../../app/utils/cytoscape-extensions';

export function defineNodeHtmlLabel(cy: cytoscape.Core){
    const labelConfig = {
        query: 'node',
        cssClass: 'cy-title',
        halign: "center",
        valign: "center",
        valignBox: "center",
        halignBox: "center",

        // @ts-ignore
        tpl: function (data) {
          const transformations = data.transformations || [];
          // @ts-ignore
          let transformationsHtml;
          
          if (transformations.length === 0) {
            // Display message when no transformations exist
            transformationsHtml = '<div class="no-transformations">NO TRANSFORMATION</div>';
          } else {
            // Display each transformation
            transformationsHtml = transformations.map((transformation: string) => `
              <div class="transformation">${transformation}</div>
            `).join('');
          }
        
          // Add the 'selected' class conditionally
          const selectedClass = data.isSelected ? 'selected' : '';
          const nodeType = data.node_type || 'NORMAL';
          
          // Determine appropriate icon and type label based on the parent datamodel type
          let iconHtml = '<i class="fas fa-table"></i>';
          let displayType = 'TBL';
          
          // Extract datamodel type if available, default to table if not specified
          const datamodelType = data.object_type || 'table';
          if (datamodelType.toLowerCase().includes('view')) {
            displayType = 'VIW';
            iconHtml = '<i class="fas fa-eye"></i>';
          } else if (datamodelType.toLowerCase().includes('proc')) {
            displayType = 'PRC';
            iconHtml = '<i class="fas fa-cogs"></i>';
          }
          
          
          // Extract column name, datamodel, schema and warehouse information
          const columnName = data.original_name || data.name || data.id || '';
          const datamodelName = data.original_datamodel_name || data.datamodel_name || '';
          
          // Extract schema and warehouse from datamodel name if available
          let warehouseName = data.database || data.warehouse || data.db || '---';
          let schemaName = data.schema || '---';
          let objectName = datamodelName;
          
          return `
            <div class="node-container ${selectedClass} ${nodeType}" data-id="${data.id}">
              <div class="node-sidebar ${nodeType}">
                ${iconHtml}
                <div class="node-type-label">${displayType}</div>
              </div>
              <div class="node-content">
                <div class="node-metadata">
                  <div class="warehouse-name">${warehouseName}</div>
                  <div class="schema-name">${schemaName}</div>
                </div>
                <div class="object-name">${objectName}</div>
                <div class="column-name">${columnName}</div>
                <div class="separator"></div>
                <div class="transformations">${transformationsHtml}</div>
              </div>
            </div>
          `;
        }
        
      };

    // @ts-ignore
    cy.nodeHtmlLabel([labelConfig]);
  }
