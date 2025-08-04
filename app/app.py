import streamlit as st
import psycopg2
import pandas as pd
from typing import List, Tuple, Optional

# Hierarchical taxonomy structure
TAXONOMY_HIERARCHY = {
    'Plantae': {
        'Tracheophyta': ['Magnoliopsida', 'Liliopsida'],
        'Magnoliophyta': ['Magnoliopsida', 'Liliopsida'],
        'Bryophyta': ['Bryopsida']
    },
    'Fungi': {
        'Basidiomycota': ['Ustilaginomycetes', 'Agaricomycetes']
    }
}

def get_database_connection():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(
            host="db",
            port="5432",
            user="postgres",
            password="example",
            database="postgres"
        )
        return conn
    except psycopg2.Error as e:
        st.error(f"Database connection error: {e}")
        return None

def get_all_records() -> Optional[List[Tuple]]:
    """Fetch all plant records from database"""
    conn = get_database_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombreplanta, precio, reino, division, clase FROM plantas ORDER BY nombreplanta")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records
    except psycopg2.Error as e:
        st.error(f"Error fetching records: {e}")
        return None

def get_filtered_records(reino: str = None, division: str = None, clase: str = None) -> Optional[List[Tuple]]:
    """Fetch filtered plant records based on taxonomy"""
    conn = get_database_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Build dynamic query based on filters
        query = "SELECT id, nombreplanta, precio, reino, division, clase FROM plantas WHERE 1=1"
        params = []
        
        if reino:
            query += " AND reino = %s"
            params.append(reino)
        if division:
            query += " AND division = %s"
            params.append(division)
        if clase:
            query += " AND clase = %s"
            params.append(clase)
            
        query += " ORDER BY nombreplanta"
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records
    except psycopg2.Error as e:
        st.error(f"Error fetching filtered records: {e}")
        return None

def add_record(nombre: str, precio: float, reino: str, division: str, clase: str) -> bool:
    """Add a new plant record to database"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO plantas (nombreplanta, precio, reino, division, clase) 
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, precio, reino, division, clase))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        st.error(f"Error adding record: {e}")
        return False

def delete_record(record_id: int) -> bool:
    """Delete a plant record by ID"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM plantas WHERE id = %s", (record_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        st.error(f"Error deleting record: {e}")
        return False

def display_records_table(records: List[Tuple]):
    """Display records in a formatted table"""
    if not records:
        st.info("No records found matching the criteria.")
        return
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(records, columns=['ID', 'Plant Name', 'Price ($)', 'Kingdom', 'Division', 'Class'])
    
    # Format price column
    df['Price ($)'] = df['Price ($)'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Show summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(records))
    with col2:
        avg_price = sum(record[2] for record in records) / len(records)
        st.metric("Average Price", f"${avg_price:.2f}")
    with col3:
        unique_kingdoms = len(set(record[3] for record in records))
        st.metric("Unique Kingdoms", unique_kingdoms)

def hierarchical_filter_sidebar():
    """Create hierarchical filter in sidebar"""
    st.sidebar.header("🔍 Filter by Taxonomy")
    
    # Kingdom selection
    kingdoms = list(TAXONOMY_HIERARCHY.keys())
    selected_kingdom = st.sidebar.selectbox(
        "Select Kingdom:",
        options=["All"] + kingdoms,
        index=0
    )
    
    selected_division = None
    selected_class = None
    
    # Division selection (depends on kingdom)
    if selected_kingdom != "All":
        divisions = list(TAXONOMY_HIERARCHY[selected_kingdom].keys())
        selected_division = st.sidebar.selectbox(
            "Select Division:",
            options=["All"] + divisions,
            index=0
        )
        
        # Class selection (depends on division)
        if selected_division != "All":
            classes = TAXONOMY_HIERARCHY[selected_kingdom][selected_division]
            selected_class = st.sidebar.selectbox(
                "Select Class:",
                options=["All"] + classes,
                index=0
            )
    
    # Convert "All" to None for database queries
    return (
        selected_kingdom if selected_kingdom != "All" else None,
        selected_division if selected_division != "All" else None,
        selected_class if selected_class != "All" else None
    )

def add_record_form():
    """Form to add new records"""
    with st.expander("➕ Add New Plant Record"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Plant Name:")
            precio = st.number_input("Price ($):", min_value=0.0, step=0.01, format="%.2f")
        
        with col2:
            # Hierarchical selection for new records
            reino = st.selectbox("Kingdom:", options=list(TAXONOMY_HIERARCHY.keys()))
            
            divisions = list(TAXONOMY_HIERARCHY[reino].keys())
            division = st.selectbox("Division:", options=divisions)
            
            classes = TAXONOMY_HIERARCHY[reino][division]
            clase = st.selectbox("Class:", options=classes)
        
        if st.button("Add Plant Record"):
            if nombre.strip():
                if add_record(nombre.strip(), precio, reino, division, clase):
                    st.success(f"Successfully added '{nombre}' to the database!")
                    st.rerun()
                else:
                    st.error("Failed to add record to database.")
            else:
                st.error("Please enter a plant name.")

def delete_records_section(records: List[Tuple]):
    """Section to delete records"""
    if not records:
        return
        
    with st.expander("🗑️ Delete Records"):
        st.warning("⚠️ This action cannot be undone!")
        
        # Create a selectbox with plant names and IDs
        record_options = {f"{record[1]} (ID: {record[0]})": record[0] for record in records}
        
        if record_options:
            selected_record = st.selectbox(
                "Select record to delete:",
                options=list(record_options.keys())
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Delete", type="secondary"):
                    record_id = record_options[selected_record]
                    if delete_record(record_id):
                        st.success("Record deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete record.")

def display_taxonomy_tree():
    """Display the taxonomy hierarchy as a tree"""
    st.sidebar.header("🌳 Taxonomy Hierarchy")
    
    for kingdom, divisions in TAXONOMY_HIERARCHY.items():
        st.sidebar.write(f"**{kingdom}**")
        for division, classes in divisions.items():
            st.sidebar.write(f"  └── {division}")
            for class_name in classes:
                st.sidebar.write(f"      └── {class_name}")

def main():
    st.set_page_config(
        page_title="Plant Database Manager",
        page_icon="🌱",
        layout="wide"
    )
    
    st.title("🌱 Plant Database Manager")
    st.markdown("---")
    
    # Sidebar filters and taxonomy tree
    reino, division, clase = hierarchical_filter_sidebar()
    st.sidebar.markdown("---")
    display_taxonomy_tree()
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("📊 Plant Records")
        
        # Show current filters
        active_filters = []
        if reino:
            active_filters.append(f"Kingdom: {reino}")
        if division:
            active_filters.append(f"Division: {division}")
        if clase:
            active_filters.append(f"Class: {clase}")
        
        if active_filters:
            st.info(f"**Active Filters:** {' → '.join(active_filters)}")
        
        # Fetch and display records
        records = get_filtered_records(reino, division, clase)
        display_records_table(records)
    
    with col2:
        st.header("🎯 Quick Stats")
        if records:
            # Kingdom distribution
            kingdom_counts = {}
            for record in records:
                kingdom = record[3]
                kingdom_counts[kingdom] = kingdom_counts.get(kingdom, 0) + 1
            
            st.subheader("By Kingdom:")
            for kingdom, count in kingdom_counts.items():
                st.write(f"• {kingdom}: {count}")
    
    st.markdown("---")
    
    # Add record form
    add_record_form()
    
    # Delete records section
    if records:
        delete_records_section(records)

if __name__ == "__main__":
    main()
