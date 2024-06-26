import React, { useState } from "react";
import axios from "axios";
import { useTable } from "react-table";
import Loader from "./components/Loader";

const App = () => {
  const [tableData, setTableData] = useState([]);
  const [showTable, setShowTable] = useState(false);
  const [loading, setLoading] = useState(false);

  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:8000/predict/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log(response);
      setTableData(response.data);
      setShowTable(true);
      setLoading(false);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Failed to upload file");
      setLoading(false);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      uploadFile(file);
    }
  };

  const columns = React.useMemo(
    () =>
      tableData.length > 0
        ? Object.keys(tableData[0]).map((key) => ({
            Header: key,
            accessor: key,
          }))
        : [],
    [tableData]
  );

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    useTable({
      columns,
      data: tableData,
    });

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="p-4">
      {!showTable ? (
        <React.Fragment>
          <label
            className="block mb-2 text-3xl text-center font-medium text-gray-900 
        dark:text-white"
            htmlFor="file_input"
          >
            Upload file
          </label>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="block w-1/2 m-auto 
        text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer 
        bg-gray-50  focus:outline-none"
            id="file_input"
          />
        </React.Fragment>
      ) : (
        <>
          <button
            className="block m-auto mb-3 border border-gray-300 rounded-lg p-2 bg-gray-50 text-gray-900"
            onClick={() => setShowTable(false)}
          >
            Upload Another CSV
          </button>
          <table
            {...getTableProps()}
            className="m-auto text-lg text-left 
          rtl:text-right divide-y divide-gray-200 
                  text-gray-500"
          >
            <thead
              className="text-xl uppercase bg-gray-50 px-6 py-3 
            text-left font-medium text-gray-500 uppercase tracking-wider"
            >
              {headerGroups.map((headerGroup) => (
                <tr {...headerGroup.getHeaderGroupProps()}>
                  {headerGroup.headers.map((column) => (
                    <th {...column.getHeaderProps()}>
                      {column.render("Header")}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody
              {...getTableBodyProps()}
              className="bg-white divide-y divide-gray-200"
            >
              {rows.map((row) => {
                prepareRow(row);
                return (
                  <tr {...row.getRowProps()}>
                    {row.cells.map((cell) => (
                      <td
                        {...cell.getCellProps()}
                        className="px-6 py-2 whitespace-nowrap"
                      >
                        {cell.render("Cell")}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
};

export default App;
